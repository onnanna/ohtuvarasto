import unittest
from app import app, warehouses, reset_app_state


class TestWebApp(unittest.TestCase):
    def setUp(self):
        """Set up test client and reset warehouses."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        reset_app_state()

    def test_index_empty(self):
        """Test index page with no warehouses."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)
        self.assertIn(b'No warehouses yet', response.data)

    def test_create_warehouse_get(self):
        """Test GET request to create warehouse page."""
        response = self.client.get('/warehouse/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse_post(self):
        """Test POST request to create a warehouse."""
        response = self.client.post('/warehouse/new', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertEqual(len(warehouses), 1)

    def test_create_warehouse_invalid_capacity(self):
        """Test creating warehouse with invalid capacity."""
        response = self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': 'invalid',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid capacity value', response.data)

    def test_create_warehouse_zero_capacity(self):
        """Test creating warehouse with zero capacity."""
        response = self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '0',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Capacity must be greater than 0', response.data)

    def test_create_warehouse_empty_name(self):
        """Test creating warehouse with empty name."""
        response = self.client.post('/warehouse/new', data={
            'name': '',
            'tilavuus': '100',
            'alku_saldo': '0'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse name is required', response.data)

    def test_view_warehouse(self):
        """Test viewing a specific warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'My Warehouse',
            'tilavuus': '100',
            'alku_saldo': '25'
        })
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Warehouse', response.data)
        self.assertIn(b'100', response.data)

    def test_view_nonexistent_warehouse(self):
        """Test viewing a warehouse that doesn't exist."""
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse not found', response.data)

    def test_add_to_warehouse(self):
        """Test adding content to warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'maara': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Added 50', response.data)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 50)

    def test_add_to_warehouse_invalid_amount(self):
        """Test adding invalid amount to warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'maara': 'invalid'
        }, follow_redirects=True)
        self.assertIn(b'Invalid amount value', response.data)

    def test_add_to_warehouse_negative_amount(self):
        """Test adding negative amount to warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'maara': '-10'
        }, follow_redirects=True)
        self.assertIn(b'Amount must be greater than 0', response.data)

    def test_add_to_full_warehouse(self):
        """Test adding content to a full warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '100'
        })
        response = self.client.post('/warehouse/1/add', data={
            'maara': '10'
        }, follow_redirects=True)
        self.assertIn(b'Warehouse is full', response.data)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 100)

    def test_remove_from_warehouse(self):
        """Test removing content from warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'maara': '30'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Removed 30', response.data)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 20)

    def test_remove_from_warehouse_invalid_amount(self):
        """Test removing invalid amount from warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'maara': 'invalid'
        }, follow_redirects=True)
        self.assertIn(b'Invalid amount value', response.data)

    def test_edit_warehouse_get(self):
        """Test GET request to edit warehouse page."""
        self.client.post('/warehouse/new', data={
            'name': 'Original Name',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Original Name', response.data)

    def test_edit_warehouse_post(self):
        """Test POST request to edit warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'Original Name',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': 'New Name'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Name', response.data)
        self.assertEqual(warehouses[1]['name'], 'New Name')

    def test_edit_warehouse_empty_name(self):
        """Test editing warehouse with empty name."""
        self.client.post('/warehouse/new', data={
            'name': 'Original Name',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': ''
        }, follow_redirects=True)
        self.assertIn(b'Warehouse name is required', response.data)

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        self.client.post('/warehouse/new', data={
            'name': 'To Delete',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(len(warehouses), 1)
        response = self.client.post('/warehouse/1/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'deleted', response.data)
        self.assertEqual(len(warehouses), 0)

    def test_delete_nonexistent_warehouse(self):
        """Test deleting a warehouse that doesn't exist."""
        response = self.client.post('/warehouse/999/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse not found', response.data)

    def test_add_to_nonexistent_warehouse(self):
        """Test adding to a warehouse that doesn't exist."""
        response = self.client.post('/warehouse/999/add', data={
            'maara': '10'
        }, follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_remove_from_nonexistent_warehouse(self):
        """Test removing from a warehouse that doesn't exist."""
        response = self.client.post('/warehouse/999/remove', data={
            'maara': '10'
        }, follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_edit_nonexistent_warehouse(self):
        """Test editing a warehouse that doesn't exist."""
        response = self.client.get('/warehouse/999/edit', follow_redirects=True)
        self.assertIn(b'Warehouse not found', response.data)

    def test_create_warehouse_invalid_initial_balance(self):
        """Test creating warehouse with invalid initial balance."""
        response = self.client.post('/warehouse/new', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid initial balance value', response.data)

    def test_multiple_warehouses(self):
        """Test creating multiple warehouses."""
        self.client.post('/warehouse/new', data={
            'name': 'Warehouse 1',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/new', data={
            'name': 'Warehouse 2',
            'tilavuus': '200',
            'alku_saldo': '50'
        })
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse 1', response.data)
        self.assertIn(b'Warehouse 2', response.data)
        self.assertEqual(len(warehouses), 2)
