// 共用JavaScript函数和功能

// DOM 加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 响应式菜单功能
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    
    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
        });
        
        // 点击菜单项后关闭菜单
        const menuItems = navbarMenu.querySelectorAll('a');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                navbarMenu.classList.remove('active');
            });
        });
    }
    
    // 模态框功能
    const modal = document.getElementById('project-modal');
    const modalOverlay = modal?.querySelector('.modal-overlay');
    const modalClose = modal?.querySelector('.modal-close');
    const projectCards = document.querySelectorAll('.project-card');
    
    if (modal && modalOverlay && modalClose) {
        // 打开模态框
        projectCards.forEach(card => {
            card.addEventListener('click', function() {
                const imageUrl = this.querySelector('.project-image img').src;
                const title = this.querySelector('.project-info h3').textContent;
                const projectData = this.querySelector('.project-data');
                const description = projectData?.querySelector('.project-details p').textContent;
                const link = projectData?.querySelector('.project-link').href;
                
                // 获取技术栈
                const techItems = projectData?.querySelectorAll('.project-tech li');
                const techList = Array.from(techItems || []).map(li => li.textContent);
                
                // 更新模态框内容
                document.getElementById('modal-project-image').src = imageUrl;
                document.getElementById('modal-project-title').textContent = title;
                document.getElementById('modal-project-description').textContent = description;
                document.getElementById('modal-project-link').href = link;
                
                // 更新技术栈列表
                const techListElement = document.getElementById('modal-project-tech');
                techListElement.innerHTML = '';
                techList.forEach(tech => {
                    const li = document.createElement('li');
                    li.textContent = tech;
                    techListElement.appendChild(li);
                });
                
                // 显示模态框
                modal.classList.add('active');
                document.body.style.overflow = 'hidden'; // 防止背景滚动
            });
        });
        
        // 关闭模态框
        function closeModal() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        modalOverlay.addEventListener('click', closeModal);
        modalClose.addEventListener('click', closeModal);
        
        // 按ESC键关闭模态框
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });
    }
    
    // 项目筛选功能
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // 更新活跃按钮状态
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                
                // 筛选项目
                projectCards.forEach(card => {
                    const categories = card.getAttribute('data-category');
                    if (filter === 'all' || categories.includes(filter)) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // 表单验证功能已移除（联系我页面已删除）
});

// 平滑滚动功能
function smoothScroll(targetId) {
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
    }
}