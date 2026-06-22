"""
WPForge 命令行入口
提供管理命令，例如创建管理员账户

用法:
    python -m app.cli create-admin --username <name> --password <pwd> --email <email>
    python -m app.cli load-demo
"""
import argparse
import sys

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User


def create_admin(username: str, password: str, email: str) -> None:
    """创建管理员用户"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing is not None:
            print(f"用户 '{username}' 已存在，跳过创建。")
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_admin=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        print(f"管理员用户 '{username}' 创建成功。")
    finally:
        db.close()


def load_demo() -> None:
    """加载示例数据（可重复执行）"""
    # 确保数据库表已创建
    init_db()

    from app.demo.demo_data import load_demo_data

    db = SessionLocal()
    try:
        stats = load_demo_data(db)
        print("=" * 50)
        print("WPForge 示例数据加载完成！")
        print("=" * 50)
        print(f"  用户:     {stats['users']} 个")
        print(f"  站点:     {stats['sites']} 个")
        print(f"  产品:     {stats['products']} 个")
        print(f"  任务:     {stats['tasks']} 个")
        print(f"  SEO设置:  {stats['seo_settings']} 条")
        print(f"  SEO审计:  {stats['seo_audits']} 条")
        print(f"  AI模型:   {stats['ai_models']} 个")
        print(f"  代理配置: {stats['proxy_configs']} 个")
        print("-" * 50)
        print("示例账号（密码统一为 Demo@123456）:")
        print("  admin   - 系统管理员")
        print("  editor  - 内容编辑")
        print("  viewer  - 只读用户")
        print("=" * 50)
    finally:
        db.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli", description="WPForge 命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    admin_parser = subparsers.add_parser("create-admin", help="创建管理员用户")
    admin_parser.add_argument("--username", required=True, help="管理员用户名")
    admin_parser.add_argument("--password", required=True, help="管理员密码")
    admin_parser.add_argument("--email", required=True, help="管理员邮箱")

    subparsers.add_parser("load-demo", help="加载示例数据（可重复执行）")

    args = parser.parse_args(argv)

    if args.command == "create-admin":
        create_admin(
            username=args.username,
            password=args.password,
            email=args.email,
        )
        return 0

    if args.command == "load-demo":
        load_demo()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
