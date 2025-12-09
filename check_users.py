from app import create_app
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"数据库中用户总数: {len(users)}")
    
    for user in users:
        print(f"- 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}")
        
    # 检查特定用户
    teacher = User.query.filter_by(username='teacher1').first()
    if teacher:
        print(f"\n找到了测试教师用户:")
        print(f"- 用户名: {teacher.username}")
        print(f"- 邮箱: {teacher.email}")
        print(f"- 角色: {teacher.role}")
        print(f"- 密码哈希: {teacher.password_hash}")
    else:
        print("\n未找到测试教师用户")