// 註解：等待 HTML 載入完成再執行，避免抓不到 DOM 元素
document.addEventListener('DOMContentLoaded', () => {
    const navList = document.getElementById('project-nav');
    const contentArea = document.getElementById('project-content');

    // 註解：向上一層的 back/data.json 請求資料
    fetch('https://test-website-f5nx.onrender.com/api/projects')
        .then(response => {
            if (!response.ok) throw new Error('資料讀取失敗');
            return response.json(); 
        })
        .then(data => {
            console.log("從雲端 API 收到的真實資料:", data);

            if (!Array.isArray(data)) {
                console.error("嚴重錯誤:API 回傳的不是陣列，無法顯示作品列");
                return; 
            }
            
            data.forEach((item, index) => {
                // 註解：建立錨點 ID，這是讓浮動島能精準跳轉的關鍵
                const sectionId = `project-sec-${index}`;

                // --- 建立左側浮動島按鈕 ---
                const li = document.createElement('li');
                li.innerHTML = `<a href="#${sectionId}" style="color: #ccc; text-decoration: none; display: block; padding: 12px 10px; transition: color 0.3s;">${item.title}</a>`;
                navList.appendChild(li);

                // --- 建立右側作品文章 ---
                const section = document.createElement('section');
                section.id = sectionId; 
                // 註解：設定底部間距，維持極簡排版
                section.style.marginBottom = '80px';
                section.style.paddingBottom = '40px';
                section.style.borderBottom = '1px solid #333';

                // 註解：判斷是否有 date，若有則渲染日期標籤
                const dateHTML = item.date ? `<p style="color: #666; font-size: 14px; margin-bottom: 20px; letter-spacing: 1px;">開發日期：${item.date}</p>` : '';

                section.innerHTML = `
                    <h2 style="color: #fff; margin-bottom: 10px; font-size: 26px;">${item.title}</h2>
                    ${dateHTML}
                    <img src="${item.image}" alt="${item.title}" style="width: 100%; max-width: 700px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #333; object-fit: cover;">
                    <p style="color: #aaa; line-height: 1.8; font-size: 16px;white-space: pre-wrap;">${item.content}</p>
                `;
                contentArea.appendChild(section);
            });
        })
        .catch(error => {
            console.error('串接錯誤:', error);
            contentArea.innerHTML = '<p style="color: #ff6b6b;">無法載入作品資料，請確認路徑或使用 Live Server 開啟。</p>';
        });
});