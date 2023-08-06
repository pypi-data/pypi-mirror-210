from course_search.course_search import search_for_courses

test_query = " I want to learn pottery "

def test_course_search(query=test_query):
    course_search_result = search_for_courses(test_query)

    assert isinstance(course_search_result, dict)
    assert len(course_search_result) == 1