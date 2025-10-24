import os
import pickle
import numpy as np
import faiss
import docx
from sentence_transformers import SentenceTransformer

def read_and_chunk_docx(folder_path):
    chunks = []
    print(f"Bắt đầu quét thư mục: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            file_path = os.path.join(folder_path, filename)
            print(f"Đang xử lý file: {filename}...")
            try:
                document = docx.Document(file_path)
                for para in document.paragraphs:
                    text = para.text.strip()
                    if len(text) > 100: # Chỉ lấy các đoạn văn có độ dài hợp lý
                        chunks.append({"source": filename, "text": text})
            except Exception as e:
                print(f"Lỗi khi đọc file {filename}: {e}")
    return chunks

def build_vector_db(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Đang mã hóa văn bản thành vector... (việc này có thể mất một lúc)")
    texts_to_embed = [chunk['text'] for chunk in chunks]
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings).astype('float32'))
    print("Đang lưu chỉ mục và dữ liệu...")
    faiss.write_index(index, 'legal_index.faiss')
    with open('legal_chunks.pkl', 'wb') as f:
        pickle.dump(chunks, f)

if __name__ == "__main__":
    documents_folder = 'documents'
    all_chunks = read_and_chunk_docx(documents_folder)
    
    if all_chunks:
        print(f"Đã trích xuất được {len(all_chunks)} đoạn văn bản từ các file .docx.")
        build_vector_db(all_chunks)
        print("Hoàn tất! Cơ sở tri thức đã sẵn sàng.")
    else:
        print("Không tìm thấy đoạn văn bản nào. Hãy kiểm tra lại thư mục 'documents' và đảm bảo có file .docx trong đó.")