import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import trafilatura 
from googleapiclient.discovery import build
from dotenv import load_dotenv
# --- 1. KHỞI TẠO ỨNG DỤNG FLASK ---
app = Flask(__name__)
CORS(app)

# --- 2. CẤU HÌNH VÀ TẢI MÔ HÌNH ---
try:
    # --- 3. ĐỌC CÁC KEY TỪ BIẾN MÔI TRƯỜNG ---
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        raise ValueError("Lỗi: GOOGLE_API_KEY hoặc SEARCH_ENGINE_ID chưa được thiết lập trong file .env")


    genai.configure(api_key=GOOGLE_API_KEY)

    print("Đang tải các mô hình...")
    model_llm = genai.GenerativeModel('gemini-2.5-flash')
    print("Tải thành công! Server đã sẵn sàng.")
except Exception as e:
    print(f"Lỗi nghiêm trọng khi khởi động server: {e}")

# --- 3. CÁC HÀM CÔNG CỤ ĐÃ NÂNG CẤP ---

def rewrite_query_with_ai(user_question):
    """(Nâng cao) Dùng AI để tối ưu hóa câu hỏi của người dùng cho việc tìm kiếm."""
    try:
        print(f"Đang tối ưu hóa câu hỏi: '{user_question}'")
        rewrite_prompt = f"Rewrite the following user question into a formal, keyword-rich search query for Vietnamese legal documents. User question: '{user_question}'"
        
        rewriter_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = rewriter_model.generate_content(rewrite_prompt)
        
        # Lấy text an toàn
        rewritten_query = response.text.strip()
        if not rewritten_query:
            return user_question # Trả về câu hỏi gốc nếu AI không trả về gì
            
        print(f"Câu hỏi đã được tối ưu thành: '{rewritten_query}'")
        return rewritten_query
    except Exception as e:
        print(f"Lỗi khi tối ưu câu hỏi, sử dụng câu hỏi gốc. Lỗi: {e}")
        return user_question # Nếu có lỗi, dùng câu hỏi gốc

def search_the_web(query):
    """Sử dụng Google Custom Search API để tìm kiếm trên web."""
    try:
        print(f"Đang tìm kiếm trên web cho: {query}")
        search_query = f"{query} site:thuvienphapluat.vn OR site:vbpl.vn OR site:luatvietnam.vn"
        
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=search_query, cx=SEARCH_ENGINE_ID, num=5).execute()
        
        urls = [item['link'] for item in res.get('items', [])]
        print(f"Đã tìm thấy các URL: {urls}")
        return urls
    except Exception as e:
        print(f"Lỗi khi tìm kiếm trên Google: {e}")
        return []

def scrape_url_content(url):
    """Sử dụng Trafilatura để trích xuất nội dung chính của trang web."""
    try:
        print(f"Đang trích xuất nội dung từ: {url}")
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=True, include_links=False)
            return text
        return None
    except Exception as e:
        print(f"Lỗi khi trích xuất URL {url}: {e}")
        return None

def generate_answer_with_prompt(question, context):
    """Sử dụng prompt đã cải tiến để tạo câu trả lời cuối cùng."""
    prompt_template_str = """You are LawStand AI, an expert legal assistant. Your goal is to be helpful, clear, and professional. You must explain complex legal topics simply and structure your answers for maximum readability.

**Thinking Process:**
1.  Analyze the user's question to understand their core need.
2.  Scan the entire context to find all relevant information.
3.  Synthesize the findings into a structured, easy-to-read answer. Start with a summary, then use headings and bullet points for details.
4.  As you write, keep track of which source URL each piece of information comes from.
5.  Apply the new citation rules to format the final answer.

**CONTEXT (Scraped from reliable legal websites):**
{context}

**MANDATORY RULES:**
1.  **Strictly Context-Based:** All factual information MUST come from the provided **CONTEXT**.
2.  **User-Friendly Presentation:** Structure the answer with a summary, clear headings, bold text for key terms, and short paragraphs. Provide a step-by-step example for calculations.
3.  **NEW CITATION STYLE (VERY IMPORTANT):**
    a. Instead of inserting full URLs in the text, use **numbered, superscript citations**, like this: `¹`, `²`, `³`.
    b. Place the citation number at the end of the sentence or paragraph that contains the information from a source.
    c. **Aggregate citations:** If an entire paragraph is synthesized from a single source, place only ONE citation number at the end of that paragraph.
    d. **At the very end of your entire response**, create a final section titled "**Nguồn Tham Khảo:**".
    e. In this section, list each number followed by its corresponding full URL.
4.  **Language Match:** Respond in the same language as the user's **QUESTION**.
5.  **Interactive Dialogue:** End your response by asking a clarifying question to encourage further interaction.

**QUESTION:**
{question}

**FINAL ANSWER (Well-structured, with superscript citations and a reference list at the end):**
"""
    final_prompt = prompt_template_str.format(context=context, question=question)
    response = model_llm.generate_content(final_prompt)
    return response.text

# --- 4. API ENDPOINT 
@app.route('/chat', methods=['POST'])
def chat_handler():
    try:
        data = request.get_json()
        user_question = data.get('contents', [])[-1]['parts'][0]['text']
        
        # B1: (Nâng cao) Dùng AI tối ưu hóa câu hỏi tìm kiếm
        search_query = rewrite_query_with_ai(user_question)
        
        # B2: Tìm kiếm trên web với câu hỏi đã tối ưu
        urls = search_the_web(search_query)
        
        # B3: Trích xuất nội dung từ các URL
        web_context = ""
        if not urls:
            web_context = "Không tìm thấy nguồn thông tin nào trên web cho câu hỏi này."
        else:
            for url in urls:
                content = scrape_url_content(url)
                if content:
                    limited_content = " ".join(content.split()[:800]) # Giới hạn 800 từ/trang
                    web_context += f"--- Nguồn: {url} ---\n{content}\n\n"
        
        # B4: Tạo câu trả lời dựa trên context từ web
        answer = generate_answer_with_prompt(user_question, web_context)
        
        response_data = {"candidates": [{"content": {"parts": [{"text": answer}], "role": "model"}}]}
        return jsonify(response_data)
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý chat: {e}")
        return jsonify({"error": {"message": "Đã có lỗi xảy ra ở server."}}), 500

# --- 5. CHẠY SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)