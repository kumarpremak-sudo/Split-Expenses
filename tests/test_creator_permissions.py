"""
Unit tests for group creator permissions and double submission prevention.
"""
import unittest
from app import create_app, db
from app.models import Group, Member, Expense
from app.routes import _is_group_creator


class TestCreatorPermissions(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SECRET_KEY'] = 'test-secret'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.g1 = Group(name='Tirupati Trip', currency='INR')
            self.g1.set_pin('1234')
            db.session.add(self.g1)
            db.session.flush()

            self.m1 = Member(group_id=self.g1.id, name='Ravi')
            self.m2 = Member(group_id=self.g1.id, name='Suresh')
            db.session.add(self.m1)
            db.session.add(self.m2)
            db.session.flush()

            self.g1.created_by_member_id = self.m1.id
            db.session.commit()

            self.group_uuid = self.g1.uuid
            self.creator_id = self.m1.id
            self.member_id = self.m2.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_is_group_creator_check(self):
        with self.app.app_context():
            group = Group.query.filter_by(uuid=self.group_uuid).first()
            creator_session = {'member_id': self.creator_id, 'member_name': 'Ravi'}
            member_session = {'member_id': self.member_id, 'member_name': 'Suresh'}

            self.assertTrue(_is_group_creator(group, creator_session))
            self.assertFalse(_is_group_creator(group, member_session))

    def test_non_creator_cannot_delete_group(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess[f'group_{self.group_uuid}'] = {
                    'member_id': self.member_id,
                    'member_name': 'Suresh',
                    'pin': '1234',
                }

            # Non-creator attempts deletion
            res = client.post(f'/group/{self.group_uuid}/delete', follow_redirects=True)
            self.assertIn(b'Only the group creator can delete this group.', res.data)

            # Verify group still exists in DB
            with self.app.app_context():
                group = Group.query.filter_by(uuid=self.group_uuid).first()
                self.assertIsNotNone(group)

    def test_creator_can_delete_group(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess[f'group_{self.group_uuid}'] = {
                    'member_id': self.creator_id,
                    'member_name': 'Ravi',
                    'pin': '1234',
                }

            res = client.post(f'/group/{self.group_uuid}/delete', follow_redirects=True)
            self.assertIn(b'permanently deleted', res.data)

            with self.app.app_context():
                group = Group.query.filter_by(uuid=self.group_uuid).first()
                self.assertIsNone(group)


if __name__ == '__main__':
    unittest.main()
