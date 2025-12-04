import pytest
import allure
import re
from pydantic import ValidationError

from models.schemas import Comment


@allure.feature("Comments")
@allure.story("Get Post Comments")
@allure.severity(allure.severity_level.CRITICAL)
class TestGetPostComments:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Get comments for a post")
    def test_get_post_comments(self, api_client, test_post_id, logger):
        with allure.step(f"GET /posts/{test_post_id}/comments"):
            response = api_client.get_post_comments(test_post_id)

        with allure.step("Validate status code"):
            assert response.status_code == 200
            allure.attach(
                str(response.status_code), "Status Code", allure.attachment_type.TEXT
            )

        with allure.step("Parse response JSON"):
            comments_data = response.json()
            assert isinstance(comments_data, list)
            assert len(comments_data) > 0

            allure.attach(
                f"Total comments: {len(comments_data)}",
                "Comments Count",
                allure.attachment_type.TEXT
            )
            logger.info(f"Retrieved {len(comments_data)} comments for post {test_post_id}")

        with allure.step("Validate Pydantic schema"):
            try:
                [Comment(**comment) for comment in comments_data]
            except ValidationError as e:
                allure.attach(str(e), "Validation Error", allure.attachment_type.TEXT)
                pytest.fail(f"Schema validation failed: {e}")

        with allure.step("Check required fields"):
            first_comment = comments_data[0]
            required_fields = ["postId", "id", "name", "email", "body"]

            for field in required_fields:
                assert field in first_comment


@allure.feature("Comments")
@allure.story("Comments Relationship")
@allure.severity(allure.severity_level.CRITICAL)
class TestCommentsPostRelationship:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Validate postId for each comment")
    def test_all_comments_belong_to_post(self, api_client, test_post_id, logger):
        response = api_client.get_post_comments(test_post_id)
        comments = response.json()

        invalid_comments = [
            {
                "comment_id": c.get("id"),
                "expected_postId": test_post_id,
                "actual_postId": c.get("postId"),
            }
            for c in comments
            if c.get("postId") != test_post_id
        ]

        if invalid_comments:
            allure.attach(
                str(invalid_comments), "Invalid Comments", allure.attachment_type.JSON
            )
            pytest.fail(f"Found {len(invalid_comments)} comments with wrong postId")

        logger.info(f"All {len(comments)} comments correctly linked to post {test_post_id}")

    @pytest.mark.regression
    @pytest.mark.parametrize("post_id", [1, 2, 3])
    @allure.title("Parameterized relationship validation")
    def test_comments_relationship_parametrized(self, api_client, post_id, logger):
        response = api_client.get_post_comments(post_id)
        comments = response.json()

        assert all(c["postId"] == post_id for c in comments)
        logger.info(f"Post {post_id} has {len(comments)} valid comments")


@allure.feature("Comments")
@allure.story("Email Validation")
@allure.severity(allure.severity_level.NORMAL)
class TestCommentEmailValidation:

    @pytest.mark.regression
    @pytest.mark.positive
    @allure.title("Validate email format in comments")
    def test_validate_comment_emails(self, api_client, test_post_id, logger):
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        response = api_client.get_post_comments(test_post_id)
        comments = response.json()

        invalid = [
            {"comment_id": c.get("id"), "email": c.get("email")}
            for c in comments
            if not email_regex.match(c.get("email", ""))
        ]

        if invalid:
            allure.attach(str(invalid), "Invalid Emails", allure.attachment_type.JSON)
            pytest.fail(f"Found {len(invalid)} invalid emails")

        logger.info(f"Validated {len(comments)} emails")

    @pytest.mark.regression
    @allure.title("Validate emails via Pydantic")
    def test_validate_emails_with_pydantic(self, api_client, test_post_id, logger):
        response = api_client.get_post_comments(test_post_id)
        comments = response.json()

        errors = []
        for comment in comments:
            try:
                Comment(**comment)
            except ValidationError as e:
                errors.append({"comment_id": comment.get("id"), "error": str(e)})

        if errors:
            allure.attach(str(errors), "Validation Errors", allure.attachment_type.JSON)
            pytest.fail(f"Pydantic validation failed for {len(errors)} comments")

        logger.info(f"All {len(comments)} comments passed Pydantic validation")


@allure.feature("Comments")
@allure.story("Comments Content")
@allure.severity(allure.severity_level.MINOR)
class TestCommentsContent:

    @pytest.mark.regression
    @allure.title("Ensure all comments contain non-empty fields")
    def test_comments_not_empty(self, api_client, test_post_id, logger):
        response = api_client.get_post_comments(test_post_id)
        comments = response.json()

        empty = []
        for c in comments:
            if not c.get("name", "").strip():
                empty.append({"comment_id": c.get("id"), "field": "name"})
            if not c.get("email", "").strip():
                empty.append({"comment_id": c.get("id"), "field": "email"})
            if not c.get("body", "").strip():
                empty.append({"comment_id": c.get("id"), "field": "body"})

        if empty:
            allure.attach(str(empty), "Empty Fields", allure.attachment_type.JSON)
            pytest.fail(f"Found {len(empty)} empty fields")

        logger.info("All comment fields contain data")

    @pytest.mark.regression
    @allure.title("Validate data types")
    def test_comment_data_types(self, api_client, test_post_id, logger):
        response = api_client.get_post_comments(test_post_id)
        comments = response.json()

        errors = []

        for c in comments:
            cid = c.get("id")

            if not isinstance(c.get("postId"), int):
                errors.append({"comment_id": cid, "field": "postId"})
            if not isinstance(c.get("id"), int):
                errors.append({"comment_id": cid, "field": "id"})
            for f in ["name", "email", "body"]:
                if not isinstance(c.get(f), str):
                    errors.append({"comment_id": cid, "field": f})

        if errors:
            allure.attach(str(errors), "Type Errors", allure.attachment_type.JSON)
            pytest.fail(f"Found {len(errors)} type errors")

        logger.info(f"Validated data types in {len(comments)} comments")


@allure.feature("Comments")
@allure.story("Comments Query")
@allure.severity(allure.severity_level.NORMAL)
class TestCommentsQuery:

    @pytest.mark.regression
    @allure.title("Get comments by query param")
    def test_get_comments_by_query_param(self, api_client, test_post_id, logger):
        response = api_client.get_comments(post_id=test_post_id)
        comments = response.json()

        assert all(c["postId"] == test_post_id for c in comments)
        logger.info(f"Retrieved {len(comments)} comments via query param")
