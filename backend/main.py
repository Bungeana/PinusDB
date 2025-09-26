from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware  # 导入 CORS 中间件
import mysql.connector
from pydantic import BaseModel
from typing import List
from Bio import SeqIO
import subprocess
import tempfile
import os
import json
from urllib.parse import quote_plus
import pandas as pd
from functools import lru_cache

app = FastAPI()

# 配置 CORS 中间件
# 允许所有来源、所有方法、所有头部信息
origins = ["*"]  # 允许所有来源，在生产环境中应设置为特定的域名

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的来源列表
    allow_credentials=True,  # 允许发送 cookie
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET, POST, PUT, DELETE等）
    allow_headers=["*"],  # 允许所有请求头
)

def get_db_connection():
    return mysql.connector.connect(
        host="114.212.172.248",
        user="test_acc",
        password="6900392",
        database="TestDB"
    )

class Protein(BaseModel):
    protein_id: str
    length: int
    file_path: str
    sequence: str = None

# 模糊搜索候选结果，用于前端搜索框提示
@app.get("/api/protein/suggest", response_model=List[str])
def suggest_proteins(q: str):  
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT protein_id FROM protein WHERE protein_id LIKE %s LIMIT 10",
        (f"%{q}%",),
    )
    results = [row["protein_id"] for row in cursor.fetchall()]  

    cursor.close()
    conn.close()
    return results

# 查询蛋白信息
@app.get("/api/protein/{protein_id}", response_model=Protein)
def get_protein(protein_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    # 精确匹配
    cursor.execute("SELECT * FROM protein WHERE protein_id = %s", (protein_id,))
    protein = cursor.fetchone()

    # 模糊匹配
    if not protein:
        fuzzy_query = f"%{protein_id}%"
        cursor.execute("SELECT * FROM protein WHERE protein_id LIKE %s LIMIT 1", (fuzzy_query,))
        protein = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {protein_id} not found")
    
    path = protein["file_path"]
    try:
        for record in SeqIO.parse(path, "fasta"):
            if record.id == protein_id:
                protein["sequence"] = str(record.seq)
                return protein
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading FASTA: {e}")

    raise HTTPException(status_code=404, detail=f"Protein {protein_id} not found in FASTA file")


# BLAST 接口
class BlastRequest(BaseModel):
    sequence: str
    program: str
    db: str         

import os

# 定义数据库基础路径
DB_BASE_PATH = "/Users/yepu/Desktop/TestDB/data"  # 这里替换成你的实际路径

def get_db_path(blast_type: str, db_name: str) -> str:
    """
    根据 BLAST 类型返回对应的数据库路径
    blastp / blastx -> protein 组
    blastn / tblastn / tblastx -> nucleotide 组
    """
    protein_group = {"blastp", "blastx"}
    nucleotide_group = {"blastn", "tblastn", "tblastx"}

    if blast_type in protein_group:
        db_group = "protein"
    elif blast_type in nucleotide_group:
        db_group = "nucleotide"
    else:
        raise ValueError(f"Unsupported BLAST type: {blast_type}")

    return os.path.join(DB_BASE_PATH, db_group, db_name)


@app.post("/api/blast")
def run_blast(request: BlastRequest):
    # 创建临时 fasta 文件
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as fasta_file:
        fasta_file.write(">query\n")
        fasta_file.write(request.sequence)
        query_path = fasta_file.name

    # 创建临时输出文件
    out_file = query_path + ".out"

    try:
        # 调用本地 BLAST
        subprocess.run(
            [
                request.program,
                "-query", query_path,
                "-db", get_db_path(request.program, request.db),
                "-out", out_file,
                "-outfmt", "6"  # 表格格式，方便解析
            ],
            check=True
        )

        # 读取结果并解析为 JSON 数组
        results = []
        with open(out_file) as f:
            for line in f:
                cols = line.strip().split("\t")
                if len(cols) >= 12:
                    results.append({
                        "query_id": cols[0],
                        "subject_id": cols[1],
                        "identity": float(cols[2]),
                        "align_length": int(cols[3]),
                        "mismatches": int(cols[4]),
                        "gap_opens": int(cols[5]),
                        "q_start": int(cols[6]),
                        "q_end": int(cols[7]),
                        "s_start": int(cols[8]),
                        "s_end": int(cols[9]),
                        "evalue": float(cols[10]),
                        "bit_score": float(cols[11])
                    })

        return {"status": "success", "results": results}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}

    finally:
        # 清理临时文件
        os.remove(query_path)
        if os.path.exists(out_file):
            os.remove(out_file)


JBROWSE_BASE = os.getenv("JBROWSE_BASE", "http://localhost:3000/")

# 物种映射：配置路径、assembly 名、初始位置、默认 tracks
SPECIES_MAP = {
    "Arabidopsis thaliana": {
        "config": "At_test/config.json",
        "assembly": "Athaliana_167_TAIR10",
        "default_loc": "Chr1:1..20000",
        "tracks": ["Athaliana_167_gene_exons.sorted.gff3"]
    }
}


@app.get("/api/jbrowse/embed")
def get_embed_url(species: str = Query("Arabidopsis thaliana")):
    """
    返回一个可直接嵌入 iframe 的 JBrowse URL
    """
    spec = SPECIES_MAP.get(species, SPECIES_MAP["Arabidopsis thaliana"])

    # 构造 session spec
    session_spec = {
        "views": [
            {
                "assembly": spec["assembly"],
                "loc": spec["default_loc"],
                "type": "LinearGenomeView",
                "tracks": spec["tracks"],
            }
        ]
    }

    # URL 编码
    payload = quote_plus(json.dumps(session_spec))

    # 拼接 URL
    url = f"{JBROWSE_BASE}?config={spec['config']}&session=spec-{payload}"

    return {
        "species": species,
        "url": url
    }

# 数据集文件映射（可以扩展）
DATASETS = {
    "E-GEOD-38612": "../data/expression/E-GEOD-38612-tpms.tsv",
    # "另一组数据示例": "path/to/other.tsv",
}

# 用缓存避免重复加载大文件
@lru_cache(maxsize=5)
def load_dataset(dataset_name: str) -> pd.DataFrame:
    if dataset_name not in DATASETS:
        raise ValueError(f"Dataset {dataset_name} not found")
    return pd.read_csv(DATASETS[dataset_name], sep="\t", index_col=0)


@app.get("/api/expression")
def get_expression(
    protein_id: str = Query("AT1G01010"),
    dataset: str = Query("E-GEOD-38612")
):
    """
    查询某个蛋白在不同组织/样品的表达量（返回数组形式）
    """
    try:
        df = pd.read_csv(DATASETS[dataset], sep="\t")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    row = df[df["GeneID"] == protein_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Protein ID {protein_id} not found in {dataset}")

    # 提取基因名，添加校验以处理没有基因名的情况
    gene_name_value = row.iloc[0]["Gene Name"]
    # 检查基因名是否存在、非空且非NaN
    if pd.isna(gene_name_value) or str(gene_name_value).strip() == '':
        gene_name = protein_id  # 如果没有基因名，使用protein_id作为替代
    else:
        gene_name = str(gene_name_value)

    # 提取表达数据（从第3列开始）
    expression_data = {}
    for col in df.columns[2:]:
        raw_value = str(row.iloc[0][col])
        # 转换成数字数组
        values = [float(v) for v in raw_value.split(",") if v.strip().isdigit()]
        expression_data[col] = values

    return {
        "dataset": dataset,
        "protein_id": protein_id,
        "gene_name": gene_name,
        "expression": expression_data
    }

# 启动 Uvicorn 服务器
# uvicorn main:app --reload

