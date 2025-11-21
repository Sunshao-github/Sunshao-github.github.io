// 共用JavaScript函数和功能

// 为卡片元素添加鼠标跟随的3D效果
function addCardHoverEffect(cards) {
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            // 获取卡片的尺寸和位置
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // 计算鼠标在卡片上的相对位置（0-1范围）
            const xPercent = x / rect.width - 0.5;
            const yPercent = y / rect.height - 0.5;
            
            // 设置旋转角度（限制最大旋转范围）
            const rotateY = xPercent * 8; // 水平旋转角度
            const rotateX = -yPercent * 8; // 垂直旋转角度
            
            // 应用3D变换
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
            
            // 添加更深的阴影效果
            card.style.boxShadow = `0 25px 40px rgba(0, 0, 0, 0.15)`;
        });
        
        // 鼠标离开时重置效果
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
            card.style.boxShadow = 'var(--shadow-soft)';
        });
    });
}

// DOM 加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 设置当前页面导航项的活动状态
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-menu a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.substring(currentPath.lastIndexOf('/') + 1) || 
            (currentPath === '/' && link.getAttribute('href') === 'index.html')) {
            // 为当前页面的导航链接添加active类
            link.classList.add('active');
        }
    });
    
    // 移动导航切换
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
            // 更新按钮图标
            const icon = navbarToggle.querySelector('i') || navbarToggle;
            if (navbarMenu.classList.contains('active')) {
                if (icon.classList.contains('fa-bars')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                }
                navbarToggle.style.backgroundColor = 'var(--secondary-color)';
                navbarToggle.style.color = 'var(--text-primary)';
            } else {
                if (icon.classList.contains('fa-times')) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
                navbarToggle.style.backgroundColor = 'var(--bg-primary)';
                navbarToggle.style.color = 'var(--text-primary)';
            }
        });
        
        // 点击菜单项后关闭菜单
        const navLinks = navbarMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navbarMenu.classList.remove('active');
                const icon = navbarToggle.querySelector('i') || navbarToggle;
                if (icon.classList.contains('fa-times')) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
                navbarToggle.style.backgroundColor = 'var(--bg-primary)';
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
    
    // 为所有卡片添加3D悬浮效果
    const allCards = document.querySelectorAll('.project-card, .timeline-content, .profile-info, .hobbies-item');
    addCardHoverEffect(allCards);
    
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
});

// 平滑滚动功能
function smoothScroll(targetId) {
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
    }
}