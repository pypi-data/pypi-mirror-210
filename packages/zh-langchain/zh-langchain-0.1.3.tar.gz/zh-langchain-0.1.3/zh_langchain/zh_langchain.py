import os
import shutil
from .chains.local_doc_qa import LocalDocQA
from .configs.model_config import *

def construct_vector_store(vs_id, files, sentence_size, history, one_conent, one_content_segmentation):
    for file in files:
        assert os.path.exists(file), "输入文件不存在"
    import nltk
    if NLTK_DATA_PATH not in nltk.data.path: nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg()
    vs_path = os.path.join(VS_ROOT_PATH, vs_id)
    filelist = []
    if not os.path.exists(os.path.join(UPLOAD_ROOT_PATH, vs_id)):
        os.makedirs(os.path.join(UPLOAD_ROOT_PATH, vs_id))
    if isinstance(files, list):
        for file in files:
            file_name = file.name if not isinstance(file, str) else file
            filename = os.path.split(file_name)[-1]
            shutil.copyfile(file_name, os.path.join(UPLOAD_ROOT_PATH, vs_id, filename))
            filelist.append(os.path.join(UPLOAD_ROOT_PATH, vs_id, filename))
        vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store(filelist, vs_path, sentence_size)
    else:
        vs_path, loaded_files = local_doc_qa.one_knowledge_add(vs_path, files, one_conent, one_content_segmentation,
                                                                sentence_size)
    if len(loaded_files):
        file_status = f"已添加 {'、'.join([os.path.split(i)[-1] for i in loaded_files if i])} 内容至知识库，并已加载知识库，请开始提问"
    else:
        file_status = "文件未成功加载，请重新上传文件"
    print(file_status)
    return local_doc_qa, vs_path


def get_prompt(query, vs_path, score_threshold=VECTOR_SEARCH_SCORE_THRESHOLD,
               vector_search_top_k=VECTOR_SEARCH_TOP_K, chunk_conent: bool = True,
               chunk_size=CHUNK_SIZE):

    resp, prompt = local_doc_qa.get_knowledge_based_conent_test(query=query, vs_path=vs_path,
                                                                score_threshold=score_threshold,
                                                                vector_search_top_k=vector_search_top_k,
                                                                chunk_conent=chunk_conent,
                                                                chunk_size=chunk_size)
    return resp, prompt

if __name__ == '__main__':

    local_doc_qa, vs_path = construct_vector_store(   
        vs_id = 'bit', 
        files=["docs/CHANGELOG.md", "docs/Issue-with-Installing-Packages-Using-pip-in-Anaconda.md"], 
        sentence_size=100,
        history=[],
        one_conent="",
        one_content_segmentation="",
    )

    resp, prompt = get_prompt(
        query = "hello world",
        vs_path = vs_path,
        score_threshold=VECTOR_SEARCH_SCORE_THRESHOLD,
        vector_search_top_k=VECTOR_SEARCH_TOP_K, 
        chunk_conent=True,
        chunk_size=CHUNK_SIZE,
    )

    print(resp)
    print(prompt)
    input()