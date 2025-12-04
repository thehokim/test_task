import pytest
import allure
import re
from pydantic import ValidationError

from models.schemas import User


@allure.feature("Users")
@allure.story("Get All Users")
@allure.severity(allure.severity_level.CRITICAL)
class TestGetUsers:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Get all users")
    def test_get_all_users(self, api_client, logger):
        response = api_client.get_users()

        assert response.status_code == 200
        allure.attach(str(response.status_code), "Status Code", allure.attachment_type.TEXT)

        users_data = response.json()
        assert isinstance(users_data, list)
        assert len(users_data) == 10

        allure.attach(f"Total users: {len(users_data)}", "Users Count", allure.attachment_type.TEXT)

        try:
            [User(**user) for user in users_data]
        except ValidationError as e:
            allure.attach(str(e), "Validation Error", allure.attachment_type.TEXT)
            pytest.fail(f"Schema validation failed: {e}")

        user_ids = [u["id"] for u in users_data]
        assert len(user_ids) == len(set(user_ids))


@allure.feature("Users")
@allure.story("Get User by ID")
@allure.severity(allure.severity_level.CRITICAL)
class TestGetUserById:

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("Get user by ID")
    def test_get_user_by_id(self, api_client, test_user_id, logger):
        response = api_client.get_user(test_user_id)

        assert response.status_code == 200

        user_data = response.json()
        try:
            user = User(**user_data)
            allure.attach(
                f"Name: {user.name}\nEmail: {user.email}\nUsername: {user.username}",
                "User Info",
                allure.attachment_type.TEXT
            )
        except ValidationError as e:
            pytest.fail(f"Schema validation failed: {e}")

        assert user_data["id"] == test_user_id

        required_fields = [
            "id", "name", "username", "email",
            "address", "phone", "website", "company"
        ]

        for field in required_fields:
            assert field in user_data


@allure.feature("Users")
@allure.story("Email Validation")
@allure.severity(allure.severity_level.NORMAL)
class TestUserEmailValidation:

    @pytest.mark.regression
    @pytest.mark.positive
    @allure.title("Validate all user emails")
    def test_validate_all_user_emails(self, api_client, logger):
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        response = api_client.get_users()
        users = response.json()

        invalid = [
            {"user_id": u.get("id"), "email": u.get("email")}
            for u in users
            if not email_regex.match(u.get("email", ""))
        ]

        if invalid:
            allure.attach(str(invalid), "Invalid Emails", allure.attachment_type.JSON)
            pytest.fail(f"Found {len(invalid)} invalid emails")

        allure.attach(
            f"Validated {len(users)} emails successfully",
            "Validation Result",
            allure.attachment_type.TEXT
        )

    @pytest.mark.regression
    @pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
    @allure.title("Validate email format for specific users")
    def test_validate_specific_user_email(self, api_client, user_id, logger):
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        response = api_client.get_user(user_id)
        user = response.json()

        assert email_regex.match(user.get("email", ""))


@allure.feature("Users")
@allure.story("Address Structure")
@allure.severity(allure.severity_level.NORMAL)
class TestUserAddressStructure:

    @pytest.mark.regression
    @pytest.mark.positive
    @allure.title("Validate user address structure")
    def test_user_address_structure(self, api_client, test_user_id, logger):
        response = api_client.get_user(test_user_id)
        user = response.json()

        assert "address" in user
        address = user["address"]

        required_address_fields = ["street", "suite", "city", "zipcode", "geo"]

        for field in required_address_fields:
            assert field in address

        geo = address["geo"]
        assert "lat" in geo and isinstance(geo["lat"], str)
        assert "lng" in geo and isinstance(geo["lng"], str)

        allure.attach(str(address), "Address Structure", allure.attachment_type.JSON)

    @pytest.mark.regression
    @allure.title("Validate all user addresses")
    def test_all_users_address_structure(self, api_client, logger):
        response = api_client.get_users()
        users = response.json()

        required_fields = ["street", "suite", "city", "zipcode", "geo"]
        invalid = []

        for user in users:
            address = user.get("address", {})
            missing = [f for f in required_fields if f not in address]

            if missing:
                invalid.append({"user_id": user.get("id"), "missing_fields": missing})
                continue

            geo = address.get("geo", {})
            if "lat" not in geo or "lng" not in geo:
                invalid.append({"user_id": user.get("id"), "issue": "invalid geo"})

        if invalid:
            allure.attach(str(invalid), "Invalid Addresses", allure.attachment_type.JSON)
            pytest.fail(f"Found {len(invalid)} invalid addresses")


@allure.feature("Users")
@allure.story("Company Information")
@allure.severity(allure.severity_level.MINOR)
class TestUserCompany:

    @pytest.mark.regression
    @allure.title("Validate user company information")
    def test_user_has_company_info(self, api_client, test_user_id, logger):
        response = api_client.get_user(test_user_id)
        user = response.json()

        assert "company" in user
        company = user["company"]

        required_company_fields = ["name", "catchPhrase", "bs"]

        for field in required_company_fields:
            assert field in company
            assert company[field]

        allure.attach(
            f"Company: {company['name']}\n"
            f"Catch Phrase: {company['catchPhrase']}\n"
            f"BS: {company['bs']}",
            "Company Info",
            allure.attachment_type.TEXT
        )