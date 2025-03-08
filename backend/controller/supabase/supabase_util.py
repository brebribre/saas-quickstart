from controller.supabase.supabase_connector import SupabaseConnector
import json

class SupabaseUtil:
    """Utility class for handling Supabase database operations."""

    def __init__(self):
        self.supabase_connector = SupabaseConnector()

    def store_products(self, user_id, data, url=None):
        """
        Inserts new products and their variants into Supabase.
        Does not update existing products or variants.

        :param user_id: The user ID associated with the products.
        :param data: A list of product and variant data.
        :param url: The URL of the product (optional).
        :return: JSON response with status and message.
        """
        if not isinstance(data, list) or len(data) == 0:
            return {"status_code": 400, "error": "Data must be a non-empty list"}, 400

        products = {}
        variants = []

        for item in data:
            item_id = item.get("item_id")
            if not item_id:
                return {"status_code": 400, "error": "Each product must have an item_id"}, 400

            # Store product if not seen before
            if item_id not in products:
                products[item_id] = {
                    "item_id": item_id,
                    "shop_id": item["shop_id"],
                    "shop_name": item["shop_name"],
                    "title": item["title"],
                    "url": url,
                    "user_id": user_id,
                    "is_price_change": False  # Always false for new products
                }

            # Collect variant data
            variant_data = {
                "item_id": item_id,
                "variant": item["variant"],
                "price": item["price"],
                "sold": item["sold"],
                "stock": item["stock"],
                "is_tracked": True,
                "is_price_change": False,  # Always false for new variants
                "user_id": user_id  # Add user_id to variant data
            }

            variants.append(variant_data)

        product_list = list(products.values())

        # Insert products
        if product_list:
            product_insert_response = self.supabase_connector.insert("products", product_list, upsert=False)
            if not product_insert_response:
                return {"status_code": 500, "error": "Failed to insert products"}, 500

        # Insert product variants
        if variants:
            variant_insert_response = self.supabase_connector.insert("product_variants", variants, upsert=False)
            if not variant_insert_response:
                return {"status_code": 500, "error": "Failed to insert product variants"}, 500

        return {"status_code": 200, "message": "Products and variants stored successfully"}, 200
    
    def get_products(self, item_id=None, user_id=None):
        """
        Fetch products along with their variants.
        
        Args:
            item_id (int, optional): Filter by product item_id
            user_id (str, optional): Filter by user_id
            
        Returns:
            list: List of products with their variants
        """
        # Fetch products based on filters
        query = self.supabase_connector.supabase.table("products").select("*")

        if item_id:
            query = query.eq("item_id", item_id)
        if user_id:
            query = query.eq("user_id", user_id)

        product_data = query.execute().data

        if not product_data:
            return []

        # Extract all item_ids for variant lookup
        item_ids = [p["item_id"] for p in product_data]

        # Fetch variants for the retrieved products
        variants_query = self.supabase_connector.supabase.table("product_variants").select("*").in_("item_id", item_ids)
        variant_data = variants_query.execute().data

        # Group variants by item_id
        variant_map = {}
        for variant in variant_data:
            item_id = variant["item_id"]
            if item_id not in variant_map:
                variant_map[item_id] = []
            variant_map[item_id].append({
                "variant_id": variant["variant_id"],
                "variant": variant["variant"],
                "price": variant["price"],
                "sold": variant["sold"],
                "stock": variant["stock"],
                "is_tracked": variant["is_tracked"]
            })

        # Combine products with their variants
        products_with_variants = []
        for product in product_data:
            product["variants"] = variant_map.get(product["item_id"], [])
            products_with_variants.append(product)

        return products_with_variants
    
    def get_variant(self, variant_id):
        """
        Retrieves a product variant by its variant_id.
        
        Args:
            variant_id (int): The ID of the variant to retrieve
            
        Returns:
            dict: The variant data or None if not found
        """
        if not variant_id:
            return None

        # Fetch the variant from the database
        variant_data = self.supabase_connector.supabase.table("product_variants").select("*").eq("variant_id", variant_id).execute().data

        if not variant_data:
            return None

        return variant_data[0]
    
    def delete_variant(self, item_id, variant_id, user_id):
        """
        Deletes a product variant from the database.
        If it's the last variant, also deletes the product.
        Also removes the variant from any tracking records.
        
        Args:
            item_id (int): The product's item_id
            variant_id (int): The variant's variant_id
            user_id (str): The user ID to verify ownership
            
        Returns:
            tuple: (success, message, status_code)
        """
        if not item_id or not variant_id or not user_id:
            return False, "Missing item_id, variant_id, or user_id", 400

        # Fetch all variants of the product by item_id
        variant_data = self.supabase_connector.supabase.table("product_variants").select("*").eq("item_id", item_id).execute().data

        if not variant_data:
            return False, "Product not found", 404

        # Check if variant exists in the variants table
        variant_to_delete = next((v for v in variant_data if v["variant_id"] == variant_id), None)

        if not variant_to_delete:
            return False, "Variant not found", 404
            
        # Check if the variant belongs to the user
        if variant_to_delete.get("user_id") != user_id:
            return False, "Unauthorized: You don't have permission to delete this variant", 403

        # Check if this variant is used as own_variant_id in any tracking
        trackings_with_own_variant = (
            self.supabase_connector.supabase.table("trackings")
            .select("tracking_id")
            .eq("own_variant_id", variant_id)
            .execute()
            .data
        )
        
        # Delete any tracking that uses this variant as own_variant_id
        for tracking in trackings_with_own_variant:
            self.delete_tracking(tracking["tracking_id"])
            
        # Check if this variant is used as a competitor variant in any tracking
        all_trackings = self.get_trackings()
        for tracking in all_trackings:
            if variant_id in tracking["competitor_variant_ids"]:
                # Remove this variant from the competitor_variant_ids list
                new_competitor_ids = [id for id in tracking["competitor_variant_ids"] if id != variant_id]
                
                # Update the tracking with the new competitor_variant_ids list
                self.supabase_connector.supabase.table("trackings").update({
                    "competitor_variant_ids": json.dumps(new_competitor_ids)
                }).eq("tracking_id", tracking["tracking_id"]).execute()

        # Delete the variant from product_variants table
        delete_response = self.supabase_connector.supabase.table("product_variants").delete().eq("variant_id", variant_id).execute()

        if not delete_response.data:
            return False, "Failed to delete variant", 500

        # Check if there are other variants left for the product
        remaining_variants = [v for v in variant_data if v["variant_id"] != variant_id]

        if not remaining_variants:
            # If no variants are left, delete the product from the products table
            delete_product_response = self.supabase_connector.supabase.table("products").delete().eq("item_id", item_id).execute()

            if not delete_product_response.data:
                return False, "Failed to delete product", 500

            return True, "Variant and product deleted successfully", 200

        # If the product still has variants, just return success for the variant deletion
        return True, "Variant deleted successfully", 200
    
    def get_trackings(self, user_id=None, tracking_id=None):
        """
        Retrieves tracking records from the trackings table.
        
        Args:
            user_id (str, optional): Filter by user_id
            tracking_id (str, optional): Filter by tracking_id
            
        Returns:
            list: List of tracking records
        """
        # Build query
        query = self.supabase_connector.supabase.table("trackings").select("*")
        
        # Apply filters if provided
        if tracking_id:
            query = query.eq("tracking_id", tracking_id)
        if user_id:
            query = query.eq("user_id", user_id)
        
        # Execute query
        response = query.execute()
        tracking_data = response.data
        
        if not tracking_data:
            return []
        
        # Process the tracking data to parse JSON strings
        processed_trackings = []
        for tracking in tracking_data:
            # Parse JSON strings
            try:
                competitor_variant_ids = json.loads(tracking.get("competitor_variant_ids", "[]"))
            except (json.JSONDecodeError, TypeError):
                competitor_variant_ids = []
                
            try:
                contact_methods = json.loads(tracking.get("contact_methods", "[]"))
            except (json.JSONDecodeError, TypeError):
                contact_methods = []
            
            # Create processed tracking object
            processed_tracking = {
                "tracking_id": tracking.get("tracking_id"),
                "user_id": tracking.get("user_id"),
                "name": tracking.get("name"),
                "own_variant_id": tracking.get("own_variant_id"),
                "competitor_variant_ids": competitor_variant_ids,
                "is_tracking": tracking.get("is_tracking", True),
                "is_price_change": tracking.get("is_price_change", False),
                "contact_methods": contact_methods,
                "created_at": tracking.get("created_at"),
                "updated_at": tracking.get("updated_at")
            }
            
            processed_trackings.append(processed_tracking)
        
        return processed_trackings
    
    def delete_tracking(self, tracking_id):
        """
        Deletes a tracking record from the trackings table.
        
        Args:
            tracking_id (str): The ID of the tracking to delete
            
        Returns:
            tuple: (success, message, status_code)
        """
        # Attempt to delete the tracking record
        delete_response = self.supabase_connector.supabase.table("trackings").delete().eq("tracking_id", tracking_id).execute()

        if not delete_response.data:
            return False, "Tracking not found", 404

        return True, "Tracking deleted successfully", 200
    
    def delete_product(self, item_id, user_id):
        """
        Deletes a product and all its variants, and updates any tracking records that reference these variants.
        
        Args:
            item_id (int): The product's item_id
            user_id (str): The user ID to verify ownership
            
        Returns:
            tuple: (success, message, status_code)
        """
        if not item_id or not user_id:
            return False, "Missing item_id or user_id", 400
            
        # First, check if the product exists and belongs to the user
        product_data = (
            self.supabase_connector.supabase.table("products")
            .select("*")
            .eq("item_id", item_id)
            .eq("user_id", user_id)
            .execute()
            .data
        )
        
        if not product_data:
            return False, "Product not found or you don't have permission to delete it", 404
            
        # Get all variants of this product
        variants_data = (
            self.supabase_connector.supabase.table("product_variants")
            .select("variant_id")
            .eq("item_id", item_id)
            .execute()
            .data
        )
        
        # Delete each variant individually to ensure proper tracking cleanup
        for variant in variants_data:
            # We don't need to check the return value for each variant deletion
            # since we're going to delete the product anyway
            self.delete_variant(item_id, variant["variant_id"], user_id)
        
        # Check if the product still exists (it might have been deleted by delete_variant)
        product_still_exists = (
            self.supabase_connector.supabase.table("products")
            .select("*")
            .eq("item_id", item_id)
            .execute()
            .data
        )
        
        # Only try to delete the product if it still exists
        if product_still_exists:
            delete_product_response = self.supabase_connector.supabase.table("products").delete().eq("item_id", item_id).execute()
            
            if not delete_product_response.data:
                return False, "Failed to delete product", 500
            
        return True, "Product and all its variants deleted successfully", 200
    
    def get_tracking_details(self, user_id=None, tracking_id=None):
        """
        Retrieves tracking records with detailed variant information.
        
        Args:
            user_id (str, optional): Filter by user_id
            tracking_id (str, optional): Filter by tracking_id
            
        Returns:
            list: List of tracking records with variant details including historical data
        """
        # Get basic tracking data
        trackings = self.get_trackings(user_id=user_id, tracking_id=tracking_id)
        if not trackings:
            return []
        
        # Collect all variant IDs
        all_variant_ids = []
        for tracking in trackings:
            if tracking["own_variant_id"]:
                all_variant_ids.append(tracking["own_variant_id"])
            all_variant_ids.extend(tracking["competitor_variant_ids"])
        
        # Remove duplicates
        unique_variant_ids = list(set(all_variant_ids))
        
        if not unique_variant_ids:
            return trackings
        
        # Fetch all variants data in one query
        variants_data = (
            self.supabase_connector.supabase.table("product_variants")
            .select("*, products(*)")
            .in_("variant_id", unique_variant_ids)
            .execute()
            .data
        )
        
        # Create a map of variant data
        variant_map = {variant["variant_id"]: variant for variant in variants_data}
        
        # Enhance tracking data with variant details
        detailed_trackings = []
        for tracking in trackings:
            detailed_tracking = tracking.copy()
            
            # Include tracking creation timestamp
            detailed_tracking["created_at"] = tracking.get("created_at")
            
            # Handle own variant details
            own_variant_id = tracking["own_variant_id"]
            last_updated_time = None
            
            if own_variant_id:
                if own_variant_id in variant_map:
                    # Use the variant data from the map
                    variant_data = variant_map[own_variant_id]
                    detailed_tracking["own_variant"] = self._create_variant_details(variant_data)
                    
                    # Get the last_updated time from the product
                    if "products" in variant_data and variant_data["products"]:
                        last_updated_time = variant_data["products"].get("last_updated")
                else:
                    # Fetch the variant details directly from the database
                    variant_data = self._fetch_variant_with_product(own_variant_id)
                    if variant_data:
                        detailed_tracking["own_variant"] = self._create_variant_details(variant_data)
                        
                        # Get the last_updated time from the product
                        if "products" in variant_data and variant_data["products"]:
                            last_updated_time = variant_data["products"].get("last_updated")
                    else:
                        # If still not found, include just the ID
                        detailed_tracking["own_variant"] = {"variant_id": own_variant_id}
            else:
                detailed_tracking["own_variant"] = None
            
            # Add competitor variants details
            competitor_variants = []
            for competitor_id in tracking["competitor_variant_ids"]:
                if competitor_id in variant_map:
                    # Use the variant data from the map
                    variant_data = variant_map[competitor_id]
                    competitor_variants.append(self._create_variant_details(variant_data))
                    
                    # If we don't have a last_updated time yet, try to get it from this competitor product
                    if not last_updated_time and "products" in variant_data and variant_data["products"]:
                        last_updated_time = variant_data["products"].get("last_updated")
                else:
                    # Fetch the variant details directly from the database
                    variant_data = self._fetch_variant_with_product(competitor_id)
                    if variant_data:
                        competitor_variants.append(self._create_variant_details(variant_data))
                        
                        # If we don't have a last_updated time yet, try to get it from this competitor product
                        if not last_updated_time and "products" in variant_data and variant_data["products"]:
                            last_updated_time = variant_data["products"].get("last_updated")
                    else:
                        # If still not found, include just the ID
                        competitor_variants.append({"variant_id": competitor_id})
            
            detailed_tracking["competitor_variants"] = competitor_variants
            
            # Use the product's last_updated time as the main last_sync_time
            # Fall back to the tracking's updated_at if no product last_updated is available
            detailed_tracking["last_sync_time"] = last_updated_time or tracking.get("updated_at")
            
            detailed_trackings.append(detailed_tracking)
        
        return detailed_trackings
        
    def _fetch_variant_with_product(self, variant_id):
        """
        Fetches a variant with its associated product details.
        
        Args:
            variant_id: The ID of the variant to fetch
            
        Returns:
            dict: The variant data with product details, or None if not found
        """
        if not variant_id:
            return None
            
        variant_data = (
            self.supabase_connector.supabase.table("product_variants")
            .select("*, products(*)")
            .eq("variant_id", variant_id)
            .execute()
            .data
        )
        
        if not variant_data:
            return None
            
        return variant_data[0]
        
    def _create_variant_details(self, variant_data):
        """
        Creates a standardized variant details object from variant data.
        
        Args:
            variant_data: The variant data from the database
            
        Returns:
            dict: Standardized variant details object
        """
        return {
            "variant_id": variant_data["variant_id"],
            "variant": variant_data["variant"],
            "price": variant_data["price"],
            "old_price": variant_data.get("old_price"),
            "sold": variant_data["sold"],
            "old_sold": variant_data.get("old_sold"),
            "stock": variant_data["stock"],
            "old_stock": variant_data.get("old_stock"),
            "is_tracked": variant_data["is_tracked"],
            "is_price_change": variant_data.get("is_price_change", False),
            "product": {
                "item_id": variant_data["products"]["item_id"],
                "shop_id": variant_data["products"]["shop_id"],
                "shop_name": variant_data["products"]["shop_name"],
                "title": variant_data["products"]["title"],
                "url": variant_data["products"]["url"]
            }
        }