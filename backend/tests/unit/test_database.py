"""
数据库操作测试
"""
import pytest
from sqlalchemy import text
from app.models import Site, Task, User
from app.core.database import get_db, Base, engine


class TestDatabaseConnection:
    """数据库连接测试"""

    def test_get_db_generator(self, db):
        """测试get_db生成器"""
        assert db is not None
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1

    def test_base_metadata_has_tables(self):
        """测试Base元数据包含表"""
        table_names = list(Base.metadata.tables.keys())
        assert "users" in table_names
        assert "sites" in table_names
        assert "tasks" in table_names


class TestUserModel:
    """用户模型测试"""

    def test_user_creation(self, db, test_user):
        """测试创建用户"""
        assert test_user.id is not None
        assert test_user.username == "testuser"
        assert test_user.email == "test@example.com"

    def test_user_query(self, db, test_user):
        """测试查询用户"""
        user = db.query(User).filter_by(username="testuser").first()
        assert user is not None
        assert user.username == "testuser"

    def test_user_update(self, db, test_user):
        """测试更新用户"""
        test_user.email = "updated@example.com"
        db.commit()
        db.refresh(test_user)
        assert test_user.email == "updated@example.com"

    def test_user_delete(self, db, test_user):
        """测试删除用户"""
        user_id = test_user.id
        db.delete(test_user)
        db.commit()
        deleted = db.query(User).filter_by(id=user_id).first()
        assert deleted is None


class TestSiteModel:
    """站点模型测试"""

    def test_site_creation(self, db, test_site):
        """测试创建站点"""
        assert test_site.id is not None
        assert test_site.name == "Test Site"
        assert test_site.url == "https://test.example.com"
        assert test_site.wp_url == "https://test.example.com"

    def test_site_query(self, db, test_site):
        """测试查询站点"""
        site = db.query(Site).filter_by(name="Test Site").first()
        assert site is not None
        assert site.name == "Test Site"

    def test_site_update(self, db, test_site):
        """测试更新站点"""
        test_site.name = "Updated Site"
        db.commit()
        db.refresh(test_site)
        assert test_site.name == "Updated Site"

    def test_site_delete(self, db, test_site):
        """测试删除站点"""
        site_id = test_site.id
        db.delete(test_site)
        db.commit()
        deleted = db.query(Site).filter_by(id=site_id).first()
        assert deleted is None

    def test_site_filter_by_status(self, db, test_site):
        """测试按状态筛选站点"""
        active_sites = db.query(Site).filter_by(status="active").all()
        assert isinstance(active_sites, list)
        assert len(active_sites) >= 1

    def test_site_filter_by_page_builder(self, db, test_site):
        """测试按页面构建器筛选站点"""
        sites = db.query(Site).filter_by(page_builder="elementor").all()
        assert isinstance(sites, list)
        assert len(sites) >= 1


class TestTaskModel:
    """任务模型测试"""

    def test_task_creation(self, db, test_user, test_site):
        """测试创建任务"""
        task = Task(
            name="Test Task",
            task_type="scrape",
            status="pending",
            progress=0,
            site_id=test_site.id,
            user_id=test_user.id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        assert task.id is not None
        assert task.name == "Test Task"
        assert task.status == "pending"

    def test_task_status_transition(self, db, test_user, test_site):
        """测试任务状态转换"""
        task = Task(
            name="Status Task",
            task_type="scrape",
            status="pending",
            progress=0,
            site_id=test_site.id,
            user_id=test_user.id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        task.status = "running"
        task.progress = 50
        db.commit()
        db.refresh(task)
        assert task.status == "running"
        assert task.progress == 50

        task.status = "completed"
        task.progress = 100
        db.commit()
        db.refresh(task)
        assert task.status == "completed"
        assert task.progress == 100

    def test_task_query_by_status(self, db, test_user, test_site):
        """测试按状态查询任务"""
        task = Task(
            name="Query Task",
            task_type="scrape",
            status="running",
            progress=30,
            site_id=test_site.id,
            user_id=test_user.id,
        )
        db.add(task)
        db.commit()

        running_tasks = db.query(Task).filter_by(status="running").all()
        assert isinstance(running_tasks, list)
        assert len(running_tasks) >= 1

    def test_task_delete(self, db, test_user, test_site):
        """测试删除任务"""
        task = Task(
            name="Delete Task",
            task_type="scrape",
            status="pending",
            progress=0,
            site_id=test_site.id,
            user_id=test_user.id,
        )
        db.add(task)
        db.commit()
        task_id = task.id

        db.delete(task)
        db.commit()
        deleted = db.query(Task).filter_by(id=task_id).first()
        assert deleted is None


class TestDatabaseTransactions:
    """数据库事务测试"""

    def test_transaction_rollback(self, db, test_user):
        """测试事务回滚"""
        savepoint = db.begin_nested()

        site = Site(
            name="Rollback Test",
            url="https://rollback.example.com",
            wp_url="https://rollback.example.com",
            wp_username="admin",
            wp_password="password",
            user_id=test_user.id,
        )
        db.add(site)
        db.flush()

        savepoint.rollback()

        site = db.query(Site).filter_by(name="Rollback Test").first()
        assert site is None

    def test_transaction_commit(self, db, test_user):
        """测试事务提交"""
        site = Site(
            name="Commit Test",
            url="https://commit.example.com",
            wp_url="https://commit.example.com",
            wp_username="admin",
            wp_password="password",
            user_id=test_user.id,
        )
        db.add(site)
        db.commit()

        site = db.query(Site).filter_by(name="Commit Test").first()
        assert site is not None

        db.delete(site)
        db.commit()


class TestDatabasePerformance:
    """数据库性能测试"""

    def test_bulk_insert(self, db, test_user):
        """测试批量插入"""
        sites = []
        for i in range(20):
            sites.append(Site(
                name=f"Bulk Site {i}",
                url=f"https://bulk{i}.example.com",
                wp_url=f"https://bulk{i}.example.com",
                wp_username="admin",
                wp_password="password",
                user_id=test_user.id,
            ))

        db.bulk_save_objects(sites)
        db.commit()

        count = db.query(Site).filter(
            Site.name.like("Bulk Site %")
        ).count()
        assert count == 20

        db.query(Site).filter(
            Site.name.like("Bulk Site %")
        ).delete()
        db.commit()

    def test_query_optimization(self, db, test_user):
        """测试查询优化"""
        for i in range(10):
            site = Site(
                name=f"Query Test {i}",
                url=f"https://query{i}.example.com",
                wp_url=f"https://query{i}.example.com",
                wp_username="admin",
                wp_password="password",
                status="active" if i % 2 == 0 else "inactive",
                user_id=test_user.id,
            )
            db.add(site)
        db.commit()

        active_sites = db.query(Site).filter_by(status="active").all()
        assert isinstance(active_sites, list)
        assert len(active_sites) >= 5

        db.query(Site).filter(
            Site.name.like("Query Test %")
        ).delete()
        db.commit()
