# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

- Dự án hoạt động theo luồng RAG (Retrieval-Augmented Generation):

1. Frontend (React): Người dùng nhập câu hỏi vào giao diện chat.
2. Backend (Python & Flask): Server nhận yêu cầu.
3. Tối ưu hóa Truy vấn: Backend sử dụng Gemini để viết lại câu hỏi của người dùng thành một truy vấn tìm kiếm giàu từ khóa.
4. Truy xuất (Retrieval): Backend sử dụng Google Custom Search API để tìm kiếm các URL liên quan từ các trang web pháp lý đã được chỉ định.
   (- https://vbpl.vn
   - https://thuvienphapluat.vn
   - https://www.quochoi.vn
   - https://moj.gov.vn)
5. Trích xuất Nội dung: Hệ thống sử dụng thư viện Trafilatura để "ghé thăm" các URL và trích xuất phần nội dung chính, loại bỏ các thành phần không cần thiết (quảng cáo, menu...).
6. Tạo sinh (Generation): Nội dung đã trích xuất được đóng gói thành {context} và chèn vào một prompt chi tiết, sau đó gửi đến Google Gemini API.
7. Phản hồi: Gemini tạo ra câu trả lời cuối cùng dựa trên context và các quy tắc đã được chỉ định (trích dẫn nguồn, định dạng...), sau đó gửi ngược lại cho giao diện người dùng hiển thị.
