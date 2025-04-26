from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from splitwise.models import Group

class SplitwiseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='ali', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_group_and_add_member_and_split(self):
        # 1. Create a group
        url_create = reverse('splitwise:create-group')
        res = self.client.post(url_create, {
            'name': 'Trip',
            'members': [self.user.id]
        })
        print("Create Group Response:", res.status_code, res.data)
        self.assertEqual(res.status_code, 201)

        group_id = res.data['id']

        # 2. Add another user
        friend = User.objects.create_user(username='friend', password='testpass')
        url_add_member = reverse('splitwise:add-member', args=[group_id])
        res = self.client.post(url_add_member, {'username': 'friend'})
        self.assertEqual(res.status_code, 200)

        # 3. Register an expense by user ali
        url_expense = reverse('splitwise:register-expense')   # اینجا فیکس شد
        res = self.client.post(url_expense, {
            'description': 'Taxi',
            'amount': 100,
            'paid_by': self.user.id,
            'group': group_id
        })
        self.assertEqual(res.status_code, 201)

        # 4. Check split result
        url_split = reverse('splitwise:split-expenses', args=[group_id])
        res = self.client.get(url_split)
        self.assertEqual(res.status_code, 200)
        self.assertIn('transactions', res.data)