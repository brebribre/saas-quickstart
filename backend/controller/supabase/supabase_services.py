import json
from datetime import datetime
from flask import current_app
from controller.supabase.supabase_connector import SupabaseConnector
from controller.apify.apify_connector import ApifyConnector
from controller.apify.apify_util import ApifyUtil
from controller.supabase.supabase_util import SupabaseUtil

class SupabaseServices:
    """
    Service class for business logic related to Supabase operations.
    This class handles complex business operations that involve multiple database operations.
    """
    
    def __init__(self):
        self.supabase_connector = SupabaseConnector()
        self.apify_connector = ApifyConnector()
        self.apify_util = ApifyUtil()
        self.supabase_util = SupabaseUtil()
    
    def sync_trackings(self, user_id):
        """
        Synchronizes tracking data by updating all related products and setting the is_price_change flag appropriately.
        
        Args:
            user_id (str): The user ID to sync trackings for
            
        Returns:
            dict: Response with status code, message, and counts of updated entities
        """
        try:
            # Step 1: Get all trackings for the user
            trackings_response = self.supabase_connector.supabase.table("trackings").select("*").eq("user_id", user_id).execute()
            trackings = trackings_response.data
            
            if not trackings:
                return {
                    "status_code": 200,
                    "message": "No trackings found for this user",
                    "updated_trackings": 0,
                    "updated_products": 0
                }
            
            # Step 2: Extract variant IDs from trackings
            all_variant_ids = []
            for tracking in trackings:
                # Add own variant ID
                if tracking.get("own_variant_id"):
                    all_variant_ids.append(tracking["own_variant_id"])
                
                # Add competitor variant IDs
                try:
                    competitor_ids = json.loads(tracking.get("competitor_variant_ids", "[]"))
                    all_variant_ids.extend(competitor_ids)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Remove duplicates
            unique_variant_ids = list(set(all_variant_ids))
            
            if not unique_variant_ids:
                return {
                    "status_code": 200,
                    "message": "No variant IDs found in trackings",
                    "updated_trackings": 0,
                    "updated_products": 0
                }
            
            # Step 3: Find product variants with these variant IDs
            variants_response = self.supabase_connector.supabase.table("product_variants").select("*").in_("variant_id", unique_variant_ids).execute()
            variants = variants_response.data
            
            if not variants:
                return {
                    "status_code": 200,
                    "message": "No variants found for the tracking IDs",
                    "updated_trackings": 0,
                    "updated_products": 0
                }
            
            # Step 4: Get unique item IDs from these variants
            item_ids = list(set([variant["item_id"] for variant in variants]))
            
            # Step 5: Find products with these item IDs and the user_id
            products_response = self.supabase_connector.supabase.table("products").select("*").in_("item_id", item_ids).eq("user_id", user_id).execute()
            products = products_response.data
            
            if not products:
                return {
                    "status_code": 200,
                    "message": "No products found for the user with the given item IDs",
                    "updated_trackings": 0,
                    "updated_products": 0
                }
            
            # Create a test client to make internal requests
            with current_app.test_client() as client:
                updated_products_count = 0
                products_with_price_changes = []
                
                # Step 6: Update each product with fresh data
                for product in products:
                    url = product.get("url")
                    if not url:
                        continue
                    
                    # Call the update endpoint for each product
                    update_response = client.put(
                        "/api/products/update/url",
                        json={"user_id": user_id, "url": url},
                        content_type="application/json"
                    )
                    
                    if update_response.status_code == 200:
                        updated_products_count += 1
                        
                        # Check if any variants had price changes
                        response_data = json.loads(update_response.data)
                        variant_changes = response_data.get("variant_changes", {})
                        
                        if variant_changes.get("updated"):
                            # If any variants were updated, check if they're in our tracking list
                            for variant_name in variant_changes.get("updated", []):
                                # Find the variant in the response data
                                for variant in response_data.get("response", []):
                                    if variant.get("variant") == variant_name:
                                        variant_id = variant.get("variant_id")
                                        if variant_id:
                                            # Check if there was a price change by comparing old_price and price
                                            if variant.get("old_price") is not None and variant.get("price") is not None and variant.get("old_price") != variant.get("price"):
                                                # Only add to price changes list if the price actually changed
                                                products_with_price_changes.append(variant_id)
                                                
                                                # Update the variant's is_price_change flag to true only for price changes
                                                self.supabase_connector.supabase.table("product_variants").update(
                                                    {"is_price_change": True}
                                                ).eq("variant_id", variant_id).execute()
                            
                            # If any variants had price changes, set the product's is_price_change flag to true
                            if products_with_price_changes:
                                self.supabase_connector.supabase.table("products").update(
                                    {"is_price_change": True}
                                ).eq("item_id", product["item_id"]).execute()
                
                # Step 7 & 8: Update tracking is_price_change flags based on product changes
                updated_trackings_count = 0
                
                for tracking in trackings:
                    tracking_has_price_change = False
                    
                    # Check if any competitor variants have price changes
                    try:
                        competitor_ids = json.loads(tracking.get("competitor_variant_ids", "[]"))
                        for competitor_id in competitor_ids:
                            if competitor_id in products_with_price_changes:
                                tracking_has_price_change = True
                                break
                    except (json.JSONDecodeError, TypeError):
                        pass
                    
                    # Update the tracking's is_price_change flag and updated_at timestamp
                    # Set updated_at to current timestamp to indicate the tracking was synced
                    # Use UTC time explicitly to avoid timezone issues
                    current_time = datetime.utcnow().isoformat()
                    update_tracking_response = self.supabase_connector.supabase.table("trackings").update({
                        "is_price_change": tracking_has_price_change,
                        "updated_at": current_time
                    }).eq("tracking_id", tracking["tracking_id"]).execute()
                    
                    if update_tracking_response.data:
                        updated_trackings_count += 1
            
            return {
                "status_code": 200,
                "message": "Tracking data synchronized successfully",
                "updated_trackings": updated_trackings_count,
                "updated_products": updated_products_count
            }
            
        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Failed to synchronize tracking data: {str(e)}"
            }
    
    def update_product_by_url(self, user_id, url):
        """
        Updates an existing product and its variants with fresh data from Shopee via Apify.
        
        Args:
            user_id (str): The user ID associated with the product
            url (str): The URL of the product to update
            
        Returns:
            dict: Response with status code, message, and updated data
        """
        try:
            # Extract shop_id and item_id from URL
            shop_id, item_id = self.apify_util.fetch_shop_and_product_id_from_url(url)
            
            if not shop_id or not item_id:
                return {"status_code": 400, "error": "Invalid Shopee URL format"}, 400
            
            # Check if product exists in database
            existing_product = (
                self.supabase_connector.supabase.table("products")
                .select("*")
                .eq("item_id", item_id)
                .execute()
                .data
            )

            if not existing_product:
                return {"status_code": 404, "error": "Product not found in database"}, 404

            # Fetch existing variants for comparison
            existing_variants = (
                self.supabase_connector.supabase.table("product_variants")
                .select("*")
                .eq("item_id", item_id)
                .execute()
                .data
            )
            
            # Create a map of existing variants by name for easy comparison
            existing_variant_map = {variant["variant"]: variant for variant in existing_variants}
            
            # Fetch fresh product details from Apify
            product_details = self.apify_connector.fetch_product_information(url)

            if not product_details:
                return {"status_code": 500, "error": "Failed to fetch product details"}, 500
            
            # Create a map of new variants by name
            new_variant_map = {item["variant"]: item for item in product_details}
            
            # Track variant changes
            variant_changes = {
                "added": [],    # New variants that didn't exist before
                "removed": [],  # Variants that no longer exist
                "updated": []   # Variants that exist but have changed data
            }
            
            # Current timestamp for last_updated
            current_time = datetime.utcnow().isoformat()
            
            # Process variants with historical data tracking
            processed_variants = []
            
            # Process existing variants that are still present (update) and new variants (add)
            for variant_name, new_data in new_variant_map.items():
                variant_data = {
                    "item_id": item_id,
                    "variant": variant_name,
                    "price": new_data["price"],
                    "stock": new_data["stock"],
                    "sold": new_data["sold"],
                    "is_tracked": True,
                    "last_updated": current_time,
                    "user_id": user_id  # Add user_id to variant data
                }
                
                # If variant already exists, preserve historical data
                if variant_name in existing_variant_map:
                    existing_data = existing_variant_map[variant_name]
                    
                    # Check if any important fields have changed
                    if (existing_data["price"] != new_data["price"] or
                        existing_data["stock"] != new_data["stock"] or
                        existing_data["sold"] != new_data["sold"]):
                        variant_changes["updated"].append(variant_name)
                    
                    # Move current values to historical fields
                    variant_data["old_price"] = existing_data["price"]
                    variant_data["old_stock"] = existing_data["stock"]
                    variant_data["old_sold"] = existing_data["sold"]
                    
                    # Preserve variant_id for existing variants
                    variant_data["variant_id"] = existing_data["variant_id"]
                else:
                    # This is a new variant
                    variant_changes["added"].append(variant_name)
                    
                    # Initialize historical data for new variants
                    variant_data["old_price"] = None
                    variant_data["old_stock"] = None
                    variant_data["old_sold"] = None
                
                processed_variants.append(variant_data)
            
            # Find removed variants
            for variant_name in existing_variant_map:
                if variant_name not in new_variant_map:
                    variant_changes["removed"].append(variant_name)
            
            # Delete existing variants for this product
            delete_variants_response = (
                self.supabase_connector.supabase.table("product_variants")
                .delete()
                .eq("item_id", item_id)
                .execute()
            )
            
            if not delete_variants_response:
                return {"status_code": 500, "error": "Failed to delete existing variants"}, 500
            
            # Insert processed variants with historical data
            if processed_variants:
                variants_insert_response = self.supabase_connector.insert("product_variants", processed_variants, upsert=True)
                if not variants_insert_response:
                    return {"status_code": 500, "error": "Failed to insert updated variants"}, 500
            
            # Update the product record with the same timestamp
            product_data = {
                "item_id": item_id,
                "shop_id": shop_id,
                "shop_name": existing_product[0]["shop_name"],
                "title": existing_product[0]["title"],
                "url": url,
                "user_id": user_id,
                "last_updated": current_time  # Using the same timestamp as variants for consistency
            }
            
            # Explicitly update the product with the new last_updated timestamp
            product_update_response = self.supabase_connector.insert("products", [product_data], upsert=True)
            if not product_update_response:
                return {"status_code": 500, "error": "Failed to update product"}, 500

            return {
                "status_code": 200,
                "message": "Product updated successfully",
                "response": processed_variants,
                "variant_changes": variant_changes,
                "last_updated": current_time  # Include the timestamp in the response
            }, 200
            
        except Exception as e:
            return {"status_code": 500, "error": f"Failed to update product: {str(e)}"}, 500
    
    def create_tracking(self, tracking_data):
        """
        Creates a new tracking record in the trackings table.
        
        Args:
            tracking_data (dict): The tracking data to insert
            
        Returns:
            dict: Response with status code, message, and tracking ID
        """
        try:
            # Format the tracking data for database insertion
            formatted_tracking = {
                "user_id": tracking_data["user_id"],
                "name": tracking_data["name"],
                "own_variant_id": tracking_data["own_product"]["variant_id"],
                "competitor_variant_ids": json.dumps([comp["variant_id"] for comp in tracking_data["competitors"]]),
                "contact_methods": json.dumps([
                    method for method, enabled in tracking_data["notification_channels"].items() if enabled
                ]),
                "is_tracking": True,
                "is_price_change": False
            }
            
            response = self.supabase_connector.supabase.table("trackings").insert(formatted_tracking).execute()
            
            if not response.data:
                return {
                    "status_code": 500,
                    "error": "Failed to create tracking"
                }, 500
            
            # Get the tracking_id from the response
            tracking_id = response.data[0]["tracking_id"] if response.data and len(response.data) > 0 else None
            
            return {
                "status_code": 201,
                "message": "Tracking created successfully",
                "tracking_id": tracking_id
            }, 201
            
        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Failed to create tracking: {str(e)}"
            }, 500

    def store_product_by_url(self, user_id, url):
        """
        Fetches product details from Shopee via Apify and stores them in Supabase.
        
        Args:
            user_id (str): The user ID to associate with the product
            url (str): The Shopee product URL
            
        Returns:
            tuple: (response_dict, status_code)
        """
        try:
            # Extract shop_id and item_id from URL
            shop_id, item_id = self.apify_util.fetch_shop_and_product_id_from_url(url)
            
            if not shop_id or not item_id:
                return {"status_code": 400, "error": "Invalid Shopee URL format"}, 400
            
            # Check if product already exists for this user
            existing_product = (
                self.supabase_connector.supabase.table("products")
                .select("*")
                .eq("item_id", item_id)
                .eq("user_id", user_id)
                .execute()
                .data
            )

            if existing_product:
                return {"status_code": 409, "error": "Product already exists for this user"}, 409

            # Fetch product details from Apify
            product_details = self.apify_connector.fetch_product_information(url)

            if not product_details:
                return {"status_code": 500, "error": "Failed to fetch product details"}, 500

            # Store in Supabase
            response, status_code = self.supabase_util.store_products(user_id, product_details, url)

            if status_code == 200:
                return {
                    "status_code": 200,
                    "message": "Product stored successfully",
                    "response": product_details
                }, 200
            else:
                return response, status_code

        except Exception as e:
            return {"status_code": 500, "error": f"Failed to store product: {str(e)}"}, 500
