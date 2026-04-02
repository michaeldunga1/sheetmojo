import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import BusinessDetails, Product, UserProfile


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductViewTests(TestCase):
	def _make_image_file(self, name='sample.jpg', size=(800, 600), image_format='JPEG'):
		buffer = BytesIO()
		Image.new('RGB', size, color=(120, 100, 180)).save(buffer, format=image_format)
		return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')

	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()
		shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

	def setUp(self):
		user_model = get_user_model()
		self.owner = user_model.objects.create_user(
			username='owner',
			email='owner@example.com',
			password='safe-password-123',
		)
		self.other_user = user_model.objects.create_user(
			username='other',
			email='other@example.com',
			password='safe-password-123',
		)
		self.business = BusinessDetails.objects.create(
			business_name='Mojo Bakery',
			category='Bakery',
			country='US',
			city='Austin',
			created_by=self.owner,
		)

	def test_owner_can_add_product(self):
		self.client.force_login(self.owner)

		response = self.client.post(
			reverse('add_product', kwargs={'slug': self.business.slug}),
			{
				'product_name': 'Sourdough Loaf',
				'product_image': self._make_image_file(),
				'product_category': 'Bread',
				'tags': 'fresh, bakery',
				'price': '8.50',
				'currency': Product.Currency.USD,
				'product_description': 'Freshly baked every morning.',
				'terms_of_sale': Product.TermsOfSale.CASH_OR_CARD,
			},
			follow=True,
		)

		self.assertRedirects(response, reverse('business_details', kwargs={'slug': self.business.slug}))
		product = Product.objects.get()
		self.assertEqual(product.business, self.business)
		self.assertEqual(product.product_name, 'Sourdough Loaf')

	def test_owner_can_edit_product(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Starter Kit',
			product_image=self._make_image_file(name='starter.jpg'),
			product_category='Baking Supplies',
			price='19.99',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		self.client.force_login(self.owner)

		response = self.client.post(
			reverse('edit_product', kwargs={'slug': self.business.slug, 'product_slug': product.slug}),
			{
				'product_name': 'Premium Starter Kit',
				'product_category': 'Baking Supplies',
				'tags': 'starter, kitchen',
				'price': '24.99',
				'currency': Product.Currency.USD,
				'product_description': 'Includes a jar and maintenance guide.',
				'terms_of_sale': Product.TermsOfSale.BANK_TRANSFER,
			},
			follow=True,
		)

		self.assertRedirects(response, reverse('business_details', kwargs={'slug': self.business.slug}))
		product.refresh_from_db()
		self.assertEqual(product.product_name, 'Premium Starter Kit')
		self.assertEqual(str(product.price), '24.99')
		self.assertEqual(product.terms_of_sale, Product.TermsOfSale.BANK_TRANSFER)

	def test_non_owner_cannot_add_product(self):
		self.client.force_login(self.other_user)

		response = self.client.get(reverse('add_product', kwargs={'slug': self.business.slug}), follow=True)

		self.assertRedirects(response, reverse('business_details', kwargs={'slug': self.business.slug}))
		self.assertEqual(Product.objects.count(), 0)

	def test_business_details_shows_product(self):
		image = SimpleUploadedFile(
			'bread.jpg',
			b'filecontent',
			content_type='image/jpeg',
		)
		Product.objects.create(
			business=self.business,
			product_name='Bread Basket',
			product_image=image,
			product_category='Bakery',
			price='12.00',
			currency=Product.Currency.USD,
			product_description='A mixed basket of artisan bread.',
			terms_of_sale=Product.TermsOfSale.PAY_ON_DELIVERY,
		)

		response = self.client.get(reverse('business_details', kwargs={'slug': self.business.slug}))

		self.assertContains(response, 'Bread Basket')
		self.assertContains(response, 'A mixed basket of artisan bread.')

	def test_product_list_page_shows_products_and_search(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Bread Basket',
			product_category='Bakery',
			price='12.00',
			currency=Product.Currency.USD,
			product_description='A mixed basket of artisan bread.',
			terms_of_sale=Product.TermsOfSale.PAY_ON_DELIVERY,
		)

		response = self.client.get(reverse('product_list'), {'q': 'Bread Basket'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'All Products')
		self.assertContains(response, product.product_name)
		self.assertContains(response, self.business.business_name)

	def test_product_detail_page_shows_product(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Coffee Beans',
			product_category='Groceries',
			price='15.75',
			currency=Product.Currency.USD,
			product_description='Single-origin beans roasted weekly.',
			terms_of_sale=Product.TermsOfSale.CASH_OR_CARD,
		)

		response = self.client.get(reverse('product_detail', kwargs={'slug': product.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Coffee Beans')
		self.assertContains(response, 'Single-origin beans roasted weekly.')
		self.assertContains(response, self.business.business_name)

	def test_products_by_category_page_filters_products(self):
		matching_product = Product.objects.create(
			business=self.business,
			product_name='Espresso Beans',
			product_category='Groceries',
			price='16.00',
			currency=Product.Currency.USD,
			product_description='Dark roast beans.',
			terms_of_sale=Product.TermsOfSale.CASH_OR_CARD,
		)
		Product.objects.create(
			business=self.business,
			product_name='Bread Knife',
			product_category='Tools',
			price='11.00',
			currency=Product.Currency.USD,
			product_description='Serrated knife.',
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		response = self.client.get(reverse('products_by_category', kwargs={'category': 'Groceries'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Groceries Products')
		self.assertContains(response, matching_product.product_name)
		self.assertNotContains(response, 'Bread Knife')

	def test_product_category_is_normalized_on_save(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Baguette',
			product_category='   bakery   goods ',
			price='5.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		self.assertEqual(product.product_category, 'Bakery Goods')

	def test_products_by_category_page_is_case_insensitive(self):
		first_product = Product.objects.create(
			business=self.business,
			product_name='Croissant',
			product_category='Bakery',
			price='4.50',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		second_product = Product.objects.create(
			business=self.business,
			product_name='Cupcake',
			product_category='Bakery',
			price='3.25',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_OR_CARD,
		)
		Product.objects.filter(pk=second_product.pk).update(product_category='bakery')

		response = self.client.get(reverse('products_by_category', kwargs={'category': 'bakery'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Bakery Products')
		self.assertContains(response, first_product.product_name)
		self.assertContains(response, second_product.product_name)

	def test_products_by_category_page_sorts_by_price_ascending(self):
		more_expensive = Product.objects.create(
			business=self.business,
			product_name='Large Cake',
			product_category='Bakery',
			price='25.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		less_expensive = Product.objects.create(
			business=self.business,
			product_name='Cookie Box',
			product_category='Bakery',
			price='7.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_OR_CARD,
		)

		response = self.client.get(reverse('products_by_category', kwargs={'category': 'Bakery'}), {'sort': 'price_asc'})

		self.assertEqual(response.status_code, 200)
		content = response.content.decode()
		self.assertLess(content.index(less_expensive.product_name), content.index(more_expensive.product_name))

	def test_products_by_category_page_sorts_by_price_descending(self):
		less_expensive = Product.objects.create(
			business=self.business,
			product_name='Bread Roll',
			product_category='Bakery',
			price='2.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		more_expensive = Product.objects.create(
			business=self.business,
			product_name='Wedding Cake',
			product_category='Bakery',
			price='120.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.BANK_TRANSFER,
		)

		response = self.client.get(reverse('products_by_category', kwargs={'category': 'Bakery'}), {'sort': 'price_desc'})

		self.assertEqual(response.status_code, 200)
		content = response.content.decode()
		self.assertLess(content.index(more_expensive.product_name), content.index(less_expensive.product_name))

	def test_product_list_filters_by_category_currency_and_price(self):
		matching = Product.objects.create(
			business=self.business,
			product_name='Filtered Match',
			product_category='Bakery',
			price='18.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		Product.objects.create(
			business=self.business,
			product_name='Wrong Currency',
			product_category='Bakery',
			price='18.00',
			currency=Product.Currency.EUR,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		Product.objects.create(
			business=self.business,
			product_name='Wrong Price',
			product_category='Bakery',
			price='45.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		response = self.client.get(reverse('product_list'), {
			'filter_category': 'bakery',
			'filter_currency': 'USD',
			'min_price': '10',
			'max_price': '20',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, matching.product_name)
		self.assertNotContains(response, 'Wrong Currency')
		self.assertNotContains(response, 'Wrong Price')

	def test_product_form_rejects_large_image(self):
		self.client.force_login(self.owner)

		buffer = BytesIO()
		Image.new('RGB', (1200, 1200), color=(255, 200, 100)).save(buffer, format='BMP')
		large_file = SimpleUploadedFile('large.bmp', buffer.getvalue(), content_type='image/bmp')
		self.assertGreater(large_file.size, 2 * 1024 * 1024)

		response = self.client.post(
			reverse('add_product', kwargs={'slug': self.business.slug}),
			{
				'product_name': 'Large Image Product',
				'product_image': large_file,
				'product_category': 'Bakery',
				'price': '9.99',
				'currency': Product.Currency.USD,
				'product_description': 'Should fail validation.',
				'terms_of_sale': Product.TermsOfSale.CASH_ONLY,
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Image file is too large. Maximum allowed size is 2 MB.')

	def test_product_thumbnail_is_generated_on_save(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Image Product',
			product_image=self._make_image_file(),
			product_category='Bakery',
			price='11.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_OR_CARD,
		)

		self.assertTrue(bool(product.product_thumbnail))
		self.assertIn('products/thumbnails/product_', product.product_thumbnail.name)
		self.assertTrue(product.product_thumbnail.name.endswith('.webp'))

	def test_product_slug_is_generated_on_save(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Special Product Name',
			product_category='Bakery',
			price='10.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		self.assertTrue(bool(product.slug))
		self.assertIn('special-product-name', product.slug)

	def test_product_detail_shows_related_products(self):
		target = Product.objects.create(
			business=self.business,
			product_name='Sourdough Loaf',
			product_category='Bakery',
			price='8.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		same_category = Product.objects.create(
			business=self.business,
			product_name='Bagel Pack',
			product_category='Bakery',
			price='6.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_OR_CARD,
		)
		other_business = BusinessDetails.objects.create(
			business_name='Mojo Cafe',
			category='Cafe',
			country='US',
			city='Austin',
			created_by=self.owner,
		)
		same_business = Product.objects.create(
			business=self.business,
			product_name='Coffee Beans',
			product_category='Groceries',
			price='15.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		unrelated = Product.objects.create(
			business=other_business,
			product_name='Tea Sachets',
			product_category='Beverages',
			price='5.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		response = self.client.get(reverse('product_detail', kwargs={'slug': target.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Related Products')
		self.assertContains(response, same_category.product_name)
		self.assertContains(response, same_business.product_name)
		self.assertNotContains(response, unrelated.product_name)
		self.assertNotContains(response, '>Sourdough Loaf</strong>')

	def test_product_list_invalid_min_price_shows_error(self):
		response = self.client.get(reverse('product_list'), {'min_price': 'abc'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Minimum price must be a valid number.')

	def test_products_by_category_invalid_price_range_shows_error(self):
		Product.objects.create(
			business=self.business,
			product_name='Range Product',
			product_category='Bakery',
			price='25.00',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		response = self.client.get(reverse('products_by_category', kwargs={'category': 'Bakery'}), {
			'min_price': '30',
			'max_price': '10',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Minimum price cannot be greater than maximum price.')

	def test_edit_product_handles_save_exception(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Starter Kit',
			product_image=self._make_image_file(name='edit-starter.jpg'),
			product_category='Bakery',
			price='19.99',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		self.client.force_login(self.owner)

		with patch('business_listing.views.edit_product.ProductForm.save', side_effect=Exception('save failed')):
			response = self.client.post(
				reverse('edit_product', kwargs={'slug': self.business.slug, 'product_slug': product.slug}),
				{
					'product_name': 'Starter Kit Updated',
					'product_category': 'Bakery',
					'tags': 'starter, updated',
					'price': '29.99',
					'currency': Product.Currency.USD,
					'product_description': 'Updated desc',
					'terms_of_sale': Product.TermsOfSale.CASH_ONLY,
				},
			)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'We could not update this product right now. Please try again.')

	def test_add_product_handles_save_exception(self):
		self.client.force_login(self.owner)

		with patch('business_listing.views.add_product.ProductForm.save', side_effect=Exception('save failed')):
			response = self.client.post(
				reverse('add_product', kwargs={'slug': self.business.slug}),
				{
					'product_name': 'New Product',
					'product_image': self._make_image_file(name='new-product.jpg'),
					'product_category': 'Bakery',
					'tags': 'new, product',
					'price': '9.99',
					'currency': Product.Currency.USD,
					'product_description': 'Desc',
					'terms_of_sale': Product.TermsOfSale.CASH_ONLY,
				},
			)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'We could not save this product right now. Please try again.')

	def test_add_product_requires_all_fields(self):
		self.client.force_login(self.owner)

		response = self.client.post(
			reverse('add_product', kwargs={'slug': self.business.slug}),
			{
				'product_name': 'Incomplete Product',
				'price': '10.00',
				'currency': Product.Currency.USD,
				'terms_of_sale': Product.TermsOfSale.CASH_ONLY,
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'This field is required.')

	def test_owner_cannot_add_more_than_ten_products(self):
		self.client.force_login(self.owner)
		for index in range(10):
			Product.objects.create(
				business=self.business,
				product_name=f'Product {index}',
				product_category='Bakery',
				price='9.99',
				currency=Product.Currency.USD,
				terms_of_sale=Product.TermsOfSale.CASH_ONLY,
			)

		response = self.client.post(
			reverse('add_product', kwargs={'slug': self.business.slug}),
			{
				'product_name': 'Overflow Product',
				'product_image': self._make_image_file(name='overflow.jpg'),
				'product_category': 'Bakery',
				'tags': 'overflow, bakery',
				'price': '11.50',
				'currency': Product.Currency.USD,
				'product_description': 'Should not be added.',
				'terms_of_sale': Product.TermsOfSale.CASH_OR_CARD,
			},
			follow=True,
		)

		self.assertRedirects(response, reverse('business_details', kwargs={'slug': self.business.slug}))
		self.assertEqual(Product.objects.filter(business=self.business).count(), 10)
		self.assertContains(response, 'maximum of 10 products')

	def test_add_product_form_redirects_when_maximum_reached(self):
		self.client.force_login(self.owner)
		for index in range(10):
			Product.objects.create(
				business=self.business,
				product_name=f'Cap Product {index}',
				product_category='Bakery',
				price='7.00',
				currency=Product.Currency.USD,
				terms_of_sale=Product.TermsOfSale.CASH_ONLY,
			)

		response = self.client.get(
			reverse('add_product', kwargs={'slug': self.business.slug}),
			follow=True,
		)

		self.assertRedirects(response, reverse('business_details', kwargs={'slug': self.business.slug}))
		self.assertContains(response, 'maximum of 10 products')

	def test_delete_product_handles_delete_exception(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Delete Target',
			product_category='Bakery',
			price='3.99',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		self.client.force_login(self.owner)

		with patch('business_listing.views.delete_product.Product.delete', side_effect=Exception('delete failed')):
			response = self.client.post(
				reverse('delete_product', kwargs={'slug': self.business.slug, 'product_slug': product.slug}),
				follow=True,
			)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Product.objects.filter(pk=product.pk).exists())

	def test_product_detail_shows_tags_as_links(self):
		product = Product.objects.create(
			business=self.business,
			product_name='Tagged Product',
			product_category='Bakery',
			tags='fresh, local',
			price='6.25',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		response = self.client.get(reverse('product_detail', kwargs={'slug': product.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('products_by_tag', kwargs={'tag': 'fresh'}))
		self.assertContains(response, reverse('products_by_tag', kwargs={'tag': 'local'}))

	def test_business_details_shows_tags_as_links(self):
		self.business.tags = 'bakery, wholesale'
		self.business.save(update_fields=['tags'])

		response = self.client.get(reverse('business_details', kwargs={'slug': self.business.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('businesses_by_tag', kwargs={'tag': 'bakery'}))
		self.assertContains(response, reverse('businesses_by_tag', kwargs={'tag': 'wholesale'}))

	def test_user_profile_shows_tags_as_links(self):
		profile, _ = UserProfile.objects.get_or_create(user=self.owner)
		profile.tags = 'mentor, remote'
		profile.save(update_fields=['tags'])

		response = self.client.get(reverse('user_profile', kwargs={'username': self.owner.username}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse('users_by_tag', kwargs={'tag': 'mentor'}))
		self.assertContains(response, reverse('users_by_tag', kwargs={'tag': 'remote'}))

	def test_products_by_tag_filters_products(self):
		matching = Product.objects.create(
			business=self.business,
			product_name='Tag Match Product',
			product_category='Bakery',
			tags='organic, farm',
			price='9.20',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)
		Product.objects.create(
			business=self.business,
			product_name='Tag Miss Product',
			product_category='Bakery',
			tags='retail',
			price='8.10',
			currency=Product.Currency.USD,
			terms_of_sale=Product.TermsOfSale.CASH_ONLY,
		)

		response = self.client.get(reverse('products_by_tag', kwargs={'tag': 'organic'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, matching.product_name)
		self.assertNotContains(response, 'Tag Miss Product')

	def test_businesses_by_tag_filters_businesses(self):
		matching = BusinessDetails.objects.create(
			business_name='Tagged Business',
			category='Bakery',
			country='US',
			city='Austin',
			tags='family, local',
			created_by=self.owner,
		)
		BusinessDetails.objects.create(
			business_name='Untagged Match',
			category='Bakery',
			country='US',
			city='Austin',
			tags='industrial',
			created_by=self.owner,
		)

		response = self.client.get(reverse('businesses_by_tag', kwargs={'tag': 'family'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, matching.business_name)
		self.assertNotContains(response, 'Untagged Match')

	def test_users_by_tag_filters_users(self):
		owner_profile, _ = UserProfile.objects.get_or_create(user=self.owner)
		owner_profile.tags = 'seller, mentor'
		owner_profile.save(update_fields=['tags'])
		other_profile, _ = UserProfile.objects.get_or_create(user=self.other_user)
		other_profile.tags = 'buyer'
		other_profile.save(update_fields=['tags'])

		response = self.client.get(reverse('users_by_tag', kwargs={'tag': 'mentor'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.owner.username)
		self.assertNotContains(response, self.other_user.username)
