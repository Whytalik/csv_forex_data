import asyncio
from typing import Dict, List, Set, Tuple
from .http_handler import HTTPHandler


class PropertiesManager:
    """Manage database properties (create, delete, check existence)."""

    def __init__(
        self, http_handler: HTTPHandler, endpoint: str, headers: dict, database_id: str
    ):
        self.http_handler = http_handler
        self.endpoint = endpoint
        self.headers = headers
        self.database_id = database_id

    async def get_properties(self) -> Dict | None:
        """Get all properties from the database"""

        async def _make_request():
            response = await self.http_handler.get(
                f"{self.endpoint}/databases/{self.database_id}",
                self.headers,
            )
            database = response.json()
            return database.get("properties", {})

        try:
            return await self.http_handler.retry_request(_make_request)
        except Exception as e:
            print(f"❌ Error fetching properties after retries: {e}")
            return None

    async def is_property_exists(self, property_name: str) -> bool:
        """Check if a property exists in the database."""
        properties = await self.get_properties()
        return properties is not None and property_name in properties

    async def create_property(
        self, property_name: str, property_type: str = "number", formula: dict = None
    ) -> bool:
        """Create a new property in the database."""
        if await self.is_property_exists(property_name):
            print(f"ℹ️ Property '{property_name}' already exists. Skipping creation.")
            return True

        try:
            properties = {property_name: {property_type: {}}}
            if property_type == "formula" and formula:
                properties[property_name] = {"formula": formula}

            response = await self.http_handler.patch(
                f"{self.endpoint}/databases/{self.database_id}",
                self.headers,
                {"properties": properties},
            )
            print(f"✅ Created property: {property_name}")
            return True
        except Exception as e:
            print(f"❌ Error creating property: {e}")
            return False

    async def delete_property(self, property_name: str) -> bool:
        """Delete a property from the database."""
        try:
            # To delete a property, we need to send a PATCH request with the property set to null
            properties = {property_name: None}

            response = await self.http_handler.patch(
                f"{self.endpoint}/databases/{self.database_id}",
                self.headers,
                {"properties": properties},
            )
            print(f"✅ Deleted property: {property_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting property '{property_name}': {e}")
            return False

    async def ensure_property_exists(
        self, property_name: str, property_type: str = "number"
    ) -> bool:
        """Ensure a property exists, create if it doesn't."""
        if await self.is_property_exists(property_name):
            print(f"ℹ️ Property '{property_name}' already exists.")
            return True
        return await self.create_property(property_name, property_type)

    async def get_number_properties(self) -> List[str]:
        """Get all number type properties from the database."""
        properties = await self.get_properties()
        if not properties:
            return []

        number_properties = []
        for prop_name, prop_config in properties.items():
            # Check if it's a number property and not a title property
            if prop_name != "title" and prop_config.get("type") == "number":
                number_properties.append(prop_name)

        return number_properties

    async def cleanup_unused_properties(self, valid_metrics: Set[str]) -> bool:
        """Remove number properties that are not in the valid metrics set."""
        try:
            existing_number_properties = await self.get_number_properties()

            # Find properties to delete (existing but not in valid metrics)
            properties_to_delete = [
                prop for prop in existing_number_properties if prop not in valid_metrics
            ]

            if not properties_to_delete:
                print("ℹ️ No unused properties found to delete")
                return True

            print(
                f"🗑️ Found {len(properties_to_delete)} unused properties to delete: {properties_to_delete}"
            )

            # Delete properties
            deletion_tasks = [
                self.delete_property(prop_name) for prop_name in properties_to_delete
            ]

            results = await asyncio.gather(*deletion_tasks, return_exceptions=True)

            successful_deletions = sum(1 for result in results if result is True)
            failed_deletions = len(results) - successful_deletions

            print(
                f"✅ Successfully deleted {successful_deletions}/{len(properties_to_delete)} unused properties"
            )
            if failed_deletions > 0:
                print(f"❌ Failed to delete {failed_deletions} properties")

            return successful_deletions == len(properties_to_delete)

        except Exception as e:
            print(f"❌ Error during property cleanup: {e}")
            return False

    async def ensure_properties_exist_batch(
        self, property_names: list[str], property_type: str = "number"
    ) -> tuple[bool, list[str]]:
        """
        Ensure multiple properties exist, creating them if necessary.
        Returns a tuple of (success, list of created properties).

        Note: This method is more efficient than calling ensure_property_exists
        multiple times because it checks all properties at once.
        """
        if not property_names:
            return True, []

        # First, get all existing properties
        properties = await self.get_properties()
        if properties is None:
            return False, []

        # Find missing properties
        missing_properties = [
            prop_name for prop_name in property_names if prop_name not in properties
        ]

        # If no properties are missing, we're done
        if not missing_properties:
            print(f"ℹ️ All {len(property_names)} properties already exist.")
            return True, []

        print(f"🔧 Creating {len(missing_properties)} missing properties in batch...")

        # Create properties in batches to avoid hitting API limits
        batch_size = 10
        created_properties = []

        for i in range(0, len(missing_properties), batch_size):
            batch = missing_properties[i : i + batch_size]

            # Create a batch of properties
            properties_dict = {}
            for prop_name in batch:
                properties_dict[prop_name] = {property_type: {}}

            try:
                await self.http_handler.patch(
                    f"{self.endpoint}/databases/{self.database_id}",
                    self.headers,
                    {"properties": properties_dict},
                )

                print(f"✅ Created properties batch {i//batch_size + 1}: {batch}")
                created_properties.extend(batch)

                # Add a small delay to avoid rate limiting
                if i + batch_size < len(missing_properties):
                    await asyncio.sleep(0.5)

            except Exception as e:
                print(f"❌ Error creating property batch: {e}")
                # Continue with next batch even if this one failed

        # Return success if all properties were created
        success = len(created_properties) == len(missing_properties)
        if success:
            print(
                f"✅ Successfully created all {len(created_properties)} missing properties"
            )
        else:
            print(
                f"⚠️ Created {len(created_properties)}/{len(missing_properties)} properties"
            )

        return success, created_properties
