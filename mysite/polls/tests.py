import datetime
from django.utils import timezone
from django.test import TestCase
from polls.models import Question
from django.urls import reverse


# Models tests
class QuestionModelTests(TestCase):
    def test_was_published_recently_futur_date(self):
        """
        Make sure it doesn't return true if the date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_old_question(self):
        """
        Should return false if question is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_fresh_question(self):
        """
        Should return true if question is less than 1 day old
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        fresh_question = Question(pub_date=time)
        self.assertIs(fresh_question.was_published_recently(), True)



# View tests
def create_question(question_text, days):
    """
    Creates a question with a given text and days offset
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions are available a text should appear
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_question(self):
        """
        Old questions are displayed on the index page
        """
        create_question('Old question', -30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Old question>'])

    def test_future_question(self):
        """
        Future questions aren't displayed on the index page
        """
        create_question('Future question', +1)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_old_questions(self):
        """
        Only old questions are displayed
        """
        create_question('Old question', -30)
        create_question('Future question', 1)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Old question>'])

    def test_multiple_questions(self):
        """
        Fresh and old questions are displayed at the same time
        """
        create_question('Old question', -30)
        create_question('Fresh question', 0)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Fresh question>','<Question: Old question>'])



class QuestionDetailViewTests(TestCase):
    def test_future_question_view(self):
        """
        Future question detail view should return 404 page
        """
        future_question = create_question('Future question', 2)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_old_question(self):
        """
        Old question should return detailed view
        """
        old_question = create_question('Old question', -30)
        response = self.client.get(reverse('polls:detail', args=(old_question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, old_question.question_text)

