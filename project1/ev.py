import os, random, string


def random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


os.environ['temp_password'] = random_string(10)
os.environ['email'] = 'book-review-no-reply@outlook.com'
os.environ['password'] = 'pTNPHetTJfhE6Ubv'
os.environ['subject'] = 'Book Review Site - Password Reset'
os.environ['message'] = 'Your Book Review Site password has been reset to a temp password. Your temp password is {} , please login using your temp password'.format(os.environ['temp_password'])


