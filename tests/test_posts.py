import pytest
import allure
from pydantic import ValidationError

from models.schemas import Post


@allure.feature("Posts")
@allure.story("Get All Posts")
@allure.severity(allure.severity_level.CRITICAL)
class TestGetPosts:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Get all posts")
    def test_get_all_posts(self, api_client, logger):
        with allure.step("GET /posts"):
            response = api_client.get_posts()

        with allure.step("Validate status code"):
            assert response.status_code == 200
            allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)

        with allure.step("Validate Content-Type"):
            assert "application/json" in response.headers.get("Content-Type", "")

        with allure.step("Parse JSON"):
            posts_data = response.json()
            assert isinstance(posts_data, list)
            assert len(posts_data) > 0

            allure.attach(f"Total posts: {len(posts_data)}", "Posts Count", allure.attachment_type.TEXT)

        with allure.step("Validate schema"):
            try:
                [Post(**post) for post in posts_data]
            except ValidationError as e:
                allure.attach(str(e), "Validation Error", allure.attachment_type.TEXT)
                pytest.fail(f"Schema validation failed: {e}")

        first_post = posts_data[0]
        assert isinstance(first_post["userId"], int)
        assert isinstance(first_post["id"], int)
        assert isinstance(first_post["title"], str)
        assert isinstance(first_post["body"], str)


@allure.feature("Posts")
@allure.story("Get Post by ID")
@allure.severity(allure.severity_level.CRITICAL)
class TestGetPostById:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Get post by ID")
    def test_get_post_by_id_positive(self, api_client, test_post_id, logger):
        response = api_client.get_post(test_post_id)

        assert response.status_code == 200

        post_data = response.json()

        try:
            Post(**post_data)
        except ValidationError as e:
            pytest.fail(f"Schema validation failed: {e}")

        assert post_data["id"] == test_post_id
        assert post_data["title"]
        assert post_data["body"]
        assert post_data["userId"] > 0

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.title("Get non-existent post")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_nonexistent_post_negative(self, api_client, logger):
        non_existent_id = 99999
        response = api_client.get_post(non_existent_id)

        assert response.status_code == 404
        logger.info(f"Received 404 for post ID {non_existent_id}")


@allure.feature("Posts")
@allure.story("Create Post")
@allure.severity(allure.severity_level.CRITICAL)
class TestCreatePost:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Create a new post")
    def test_create_post(self, api_client, test_post_data, logger):
        allure.attach(str(test_post_data), "Request Body", allure.attachment_type.JSON)

        response = api_client.create_post(
            title=test_post_data["title"],
            body=test_post_data["body"],
            user_id=test_post_data["userId"]
        )

        assert response.status_code == 201

        created_post = response.json()

        assert created_post["title"] == test_post_data["title"]
        assert created_post["body"] == test_post_data["body"]
        assert created_post["userId"] == test_post_data["userId"]

        assert "id" in created_post and isinstance(created_post["id"], int)

        logger.info(f"Post created with ID: {created_post['id']}")
        allure.attach(str(created_post["id"]), "Created Post ID", allure.attachment_type.TEXT)


@allure.feature("Posts")
@allure.story("Update Post")
@allure.severity(allure.severity_level.NORMAL)
class TestUpdatePost:

    @pytest.mark.regression
    @pytest.mark.positive
    @allure.title("Update an existing post")
    def test_update_post(self, api_client, test_post_id, logger):
        updated_data = {
            "title": "Updated Test Post",
            "body": "This post has been updated during testing",
            "userId": 1
        }

        allure.attach(str(updated_data), "Updated Data", allure.attachment_type.JSON)

        response = api_client.update_post(
            post_id=test_post_id,
            title=updated_data["title"],
            body=updated_data["body"],
            user_id=updated_data["userId"]
        )

        assert response.status_code == 200

        updated_post = response.json()

        assert updated_post["id"] == test_post_id
        assert updated_post["title"] == updated_data["title"]
        assert updated_post["body"] == updated_data["body"]
        assert updated_post["userId"] == updated_data["userId"]

        logger.info(f"Post {test_post_id} updated successfully")


@allure.feature("Posts")
@allure.story("Delete Post")
@allure.severity(allure.severity_level.NORMAL)
class TestDeletePost:

    @pytest.mark.regression
    @pytest.mark.positive
    @allure.title("Delete a post")
    def test_delete_post(self, api_client, test_post_id, logger):
        response = api_client.delete_post(test_post_id)

        assert response.status_code == 200

        deleted = response.json()
        assert deleted == {}

        logger.info(f"Post {test_post_id} deleted successfully")


@allure.feature("Posts")
@allure.story("Parametrized Tests")
@allure.severity(allure.severity_level.MINOR)
class TestParametrizedPosts:

    @pytest.mark.regression
    @pytest.mark.parametrize("post_id", [1, 2, 3, 5, 10])
    @allure.title("Get posts by multiple IDs")
    def test_get_multiple_posts_by_id(self, api_client, post_id, logger):
        response = api_client.get_post(post_id)

        assert response.status_code == 200
        post_data = response.json()

        post = Post(**post_data)
        assert post.id == post_id

        logger.info(f"Post {post_id} validated: {post.title}")

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "user_id,expected_posts",
        [
            (1, 10),
            (2, 10),
        ]
    )
    @allure.title("Validate post count per user")
    def test_posts_count_by_user(self, api_client, user_id, expected_posts, logger):
        response = api_client.get_posts(user_id=user_id)

        assert response.status_code == 200

        posts = response.json()
        assert len(posts) == expected_posts

        logger.info(f"User {user_id} has {len(posts)} posts")
