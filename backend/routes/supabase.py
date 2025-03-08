from flask import Blueprint, jsonify, request
from flasgger import swag_from
from controller.supabase.supabase_services import SupabaseServices
from controller.supabase.supabase_util import SupabaseUtil

supabase_bp = Blueprint("supabase", __name__)
supabase_services = SupabaseServices()
supabase_util = SupabaseUtil()

@supabase_bp.route("/api/products", methods=["GET"])
@swag_from(
    {
        "tags": ["Products"],
        "parameters": [
            {
                "name": "item_id",
                "in": "query",
                "type": "integer",
                "required": False,
                "description": "Filter by product item_id",
                "example": 24256522593
            },
            {
                "name": "user_id",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Filter by user_id (fetch products by user)",
                "example": "550e8400-e29b-41d4-a716-446655440000"
            }
        ],
        "responses": {
            200: {
                "description": "List of products with variants",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "products": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "integer"},
                                    "shop_id": {"type": "integer"},
                                    "shop_name": {"type": "string"},
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "last_updated": {"type": "string", "example": "2023-07-01T12:34:56.789Z"},
                                    "variants": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "variant_id": {"type": "integer"},
                                                "variant": {"type": "string"},
                                                "price": {"type": "number"},
                                                "sold": {"type": "integer"},
                                                "stock": {"type": "integer"},
                                                "is_tracked": {"type": "boolean"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }
)
def get_products():
    """Fetch products along with their variants."""
    item_id = request.args.get("item_id", type=int)
    user_id = request.args.get("user_id", type=str)

    products = supabase_util.get_products(item_id=item_id, user_id=user_id)
    return jsonify({"status_code": 200, "products": products})

@supabase_bp.route("/api/products/store", methods=["POST"])
@swag_from(
    {
        "tags": ["Products"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "example": "550e8400-e29b-41d4-a716-446655440000"},
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "integer"},
                                    "shop_id": {"type": "integer"},
                                    "shop_name": {"type": "string"},
                                    "title": {"type": "string"},
                                    "variant": {"type": "string"},
                                    "price": {"type": "number"},
                                    "sold": {"type": "integer"},
                                    "stock": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "required": ["user_id", "data"]
                }
            }
        ],
        "responses": {
            200: {
                "description": "Products stored successfully",
                "schema": {
                    "type": "object",
                    "properties": {"status_code": {"type": "integer", "example": 200}},
                },
            },
            400: {
                "description": "Invalid input",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 400},
                        "error": {"type": "string", "example": "Missing user_id or invalid data format"},
                    },
                },
            }
        },
    }
)
def store_products():
    """Inserts new products and their variants into Supabase."""
    request_data = request.get_json()

    if not isinstance(request_data, dict) or "user_id" not in request_data or "data" not in request_data:
        return jsonify({"status_code": 400, "error": "Missing user_id or invalid data format"}), 400

    user_id = request_data["user_id"]
    data = request_data["data"]

    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"status_code": 400, "error": "Data must be a non-empty list"}), 400

    response, status_code = supabase_util.store_products(user_id, data)
    return jsonify(response), status_code

@supabase_bp.route("/api/products/store/url", methods=["POST"])
@swag_from(
    {
        "tags": ["Products"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "example": "550e8400-e29b-41d4-a716-446655440000"},
                        "url": {
                            "type": "string",
                            "example": "https://shopee.co.id/product-i.1111166168.24256522593"
                        }
                    },
                    "required": ["user_id", "url"]
                }
            }
        ],
        "responses": {
            200: {
                "description": "Product details fetched and stored successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "message": {"type": "string", "example": "Product stored successfully"},
                        "response": {"type": "object"}
                    }
                },
            },
            400: {"description": "Bad Request"},
            500: {"description": "Internal Server Error"}
        },
    }
)
def store_product_by_url():
    """Fetches product details from Shopee via Apify, then stores them in Supabase."""
    request_data = request.get_json()

    if not isinstance(request_data, dict) or "user_id" not in request_data or "url" not in request_data:
        return jsonify({"status_code": 400, "error": "URL and user_id are required"}), 400

    url = request_data["url"]
    user_id = request_data["user_id"]

    response, status_code = supabase_services.store_product_by_url(user_id, url)
    return jsonify(response), status_code

@supabase_bp.route("/api/products/variant", methods=["GET"])
@swag_from(
    {
        "tags": ["Variants"],
        "parameters": [
            {
                "name": "variant_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of the product variant to retrieve",
                "example": 123456
            }
        ],
        "responses": {
            200: {
                "description": "Variant retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "variant": {
                            "type": "object",
                            "properties": {
                                "variant_id": {"type": "integer"},
                                "item_id": {"type": "integer"},
                                "variant": {"type": "string"},
                                "price": {"type": "number"},
                                "old_price": {"type": "number"},
                                "sold": {"type": "integer"},
                                "old_sold": {"type": "integer"},
                                "stock": {"type": "integer"},
                                "old_stock": {"type": "integer"},
                                "is_tracked": {"type": "boolean"},
                                "is_price_change": {"type": "boolean"},
                                "product": {
                                    "type": "object",
                                    "properties": {
                                        "item_id": {"type": "integer"},
                                        "shop_id": {"type": "integer"},
                                        "shop_name": {"type": "string"},
                                        "title": {"type": "string"},
                                        "url": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            404: {"description": "Variant not found"}
        },
    }
)
def get_variant():
    """Retrieves a product variant by its variant_id."""
    variant_id = request.args.get("variant_id", type=int)

    if not variant_id:
        return jsonify({"status_code": 400, "error": "Missing variant_id"}), 400

    variant = supabase_util.get_variant(variant_id)
    if not variant:
        return jsonify({"status_code": 404, "error": "Variant not found"}), 404

    return jsonify({"status_code": 200, "variant": variant}), 200

@supabase_bp.route("/api/products/variant", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Variants"],
        "parameters": [
            {
                "name": "item_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of the product",
                "example": 24256522593
            },
            {
                "name": "variant_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of the product variant to delete",
                "example": 123456
            },
            {
                "name": "user_id",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "ID of the user who owns the variant",
                "example": "550e8400-e29b-41d4-a716-446655440000"
            }
        ],
        "responses": {
            200: {
                "description": "Product variant deleted successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "message": {"type": "string", "example": "Variant deleted successfully"}
                    }
                }
            },
            403: {"description": "Unauthorized - User doesn't own this variant"},
            404: {"description": "Variant or product not found"},
            409: {"description": "Conflict - Cannot delete the last variant"}
        },
    }
)
def delete_variant():
    """Deletes a product variant from the database."""
    item_id = request.args.get("item_id", type=int)
    variant_id = request.args.get("variant_id", type=int)
    user_id = request.args.get("user_id", type=str)

    if not item_id or not variant_id or not user_id:
        return jsonify({"status_code": 400, "error": "Missing item_id, variant_id, or user_id"}), 400

    success, message, status_code = supabase_util.delete_variant(item_id, variant_id, user_id)
    return jsonify({"status_code": status_code, "message" if success else "error": message}), status_code

@supabase_bp.route("/api/products/update/url", methods=["PUT"])
@swag_from(
    {
        "tags": ["Products"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "example": "550e8400-e29b-41d4-a716-446655440000"},
                        "url": {
                            "type": "string",
                            "example": "https://shopee.co.id/product-i.1111166168.24256522593"
                        }
                    },
                    "required": ["user_id", "url"]
                }
            }
        ],
        "responses": {
            200: {
                "description": "Product details updated successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "message": {"type": "string", "example": "Product updated successfully"},
                        "response": {"type": "object"},
                        "variant_changes": {
                            "type": "object",
                            "properties": {
                                "added": {"type": "array", "items": {"type": "string"}},
                                "removed": {"type": "array", "items": {"type": "string"}},
                                "updated": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                },
            },
            400: {"description": "Bad Request"},
            404: {"description": "Product not found"},
            500: {"description": "Internal Server Error"}
        },
    }
)
def update_product_by_url():
    """Updates an existing product and its variants with fresh data from Shopee."""
    request_data = request.get_json()

    if not isinstance(request_data, dict) or "user_id" not in request_data or "url" not in request_data:
        return jsonify({"status_code": 400, "error": "URL and user_id are required"}), 400

    url = request_data["url"]
    user_id = request_data["user_id"]

    response, status_code = supabase_services.update_product_by_url(user_id, url)
    return jsonify(response), status_code

@supabase_bp.route("/api/trackings", methods=["POST"])
@swag_from(
    {
        "tags": ["Trackings"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "name": {"type": "string"},
                        "own_product": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "integer"},
                                "variant_id": {"type": "integer"}
                            }
                        },
                        "competitors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "integer"},
                                    "variant_id": {"type": "integer"}
                                }
                            }
                        },
                        "notification_channels": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "boolean"},
                                "telegram": {"type": "boolean"},
                                "website": {"type": "boolean"}
                            }
                        }
                    },
                    "required": ["user_id", "name", "own_product", "competitors", "notification_channels"]
                }
            }
        ],
        "responses": {
            201: {"description": "Tracking created successfully"},
            400: {"description": "Bad Request"},
            500: {"description": "Internal Server Error"}
        }
    }
)
def create_tracking():
    """Creates a new tracking record."""
    request_data = request.get_json()
    
    # Validate required fields
    required_fields = ["user_id", "name", "own_product", "competitors", "notification_channels"]
    for field in required_fields:
        if field not in request_data:
            return jsonify({
                "status_code": 400,
                "error": f"Missing required field: {field}"
            }), 400
    
    response, status_code = supabase_services.create_tracking(request_data)
    return jsonify(response), status_code

@supabase_bp.route("/api/trackings", methods=["GET"])
@swag_from(
    {
        "tags": ["Trackings"],
        "parameters": [
            {
                "name": "user_id",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Filter trackings by user_id"
            },
            {
                "name": "tracking_id",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Get a specific tracking by ID"
            }
        ],
        "responses": {
            200: {"description": "List of tracking records"},
            404: {"description": "No trackings found"}
        }
    }
)
def get_trackings():
    """Retrieves tracking records from the database."""
    user_id = request.args.get("user_id")
    tracking_id = request.args.get("tracking_id")
    
    trackings = supabase_util.get_trackings(user_id=user_id, tracking_id=tracking_id)
    return jsonify({"status_code": 200, "trackings": trackings})

@supabase_bp.route("/api/trackings/<tracking_id>", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Trackings"],
        "parameters": [
            {
                "name": "tracking_id",
                "in": "path",
                "type": "string",
                "required": True,
                "description": "ID of the tracking record to delete"
            }
        ],
        "responses": {
            200: {"description": "Tracking deleted successfully"},
            404: {"description": "Tracking not found"},
            500: {"description": "Internal Server Error"}
        },
    }
)
def delete_tracking(tracking_id):
    """Deletes a tracking record from the database."""
    success, message, status_code = supabase_util.delete_tracking(tracking_id)
    return jsonify({"status_code": status_code, "message" if success else "error": message}), status_code

@supabase_bp.route("/api/trackings/sync", methods=["POST"])
@swag_from(
    {
        "tags": ["Trackings"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"}
                    },
                    "required": ["user_id"]
                }
            }
        ],
        "responses": {
            200: {"description": "Tracking data synchronized successfully"},
            400: {"description": "Bad Request"},
            500: {"description": "Internal Server Error"}
        }
    }
)
def sync_trackings():
    """Synchronizes tracking data by updating all related products."""
    request_data = request.get_json()
    
    if not isinstance(request_data, dict) or "user_id" not in request_data:
        return jsonify({"status_code": 400, "error": "Missing user_id"}), 400
    
    user_id = request_data["user_id"]
    response = supabase_services.sync_trackings(user_id)
    
    return jsonify(response)

@supabase_bp.route("/api/trackings/details", methods=["GET"])
@swag_from(
    {
        "tags": ["Trackings"],
        "parameters": [
            {
                "name": "user_id",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Filter trackings by user_id"
            },
            {
                "name": "tracking_id",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Get a specific tracking by ID"
            }
        ],
        "responses": {
            200: {
                "description": "List of tracking records with variant details",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "trackings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tracking_id": {"type": "string"},
                                    "user_id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "own_variant": {
                                        "type": "object",
                                        "properties": {
                                            "variant_id": {"type": "integer"},
                                            "variant": {"type": "string"},
                                            "price": {"type": "number"},
                                            "old_price": {"type": "number"},
                                            "sold": {"type": "integer"},
                                            "old_sold": {"type": "integer"},
                                            "stock": {"type": "integer"},
                                            "old_stock": {"type": "integer"},
                                            "is_tracked": {"type": "boolean"},
                                            "is_price_change": {"type": "boolean"},
                                            "product": {
                                                "type": "object",
                                                "properties": {
                                                    "item_id": {"type": "integer"},
                                                    "shop_id": {"type": "integer"},
                                                    "shop_name": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "url": {"type": "string"}
                                                }
                                            }
                                        }
                                    },
                                    "competitor_variants": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "variant_id": {"type": "integer"},
                                                "variant": {"type": "string"},
                                                "price": {"type": "number"},
                                                "old_price": {"type": "number"},
                                                "sold": {"type": "integer"},
                                                "old_sold": {"type": "integer"},
                                                "stock": {"type": "integer"},
                                                "old_stock": {"type": "integer"},
                                                "is_tracked": {"type": "boolean"},
                                                "is_price_change": {"type": "boolean"},
                                                "product": {
                                                    "type": "object",
                                                    "properties": {
                                                        "item_id": {"type": "integer"},
                                                        "shop_id": {"type": "integer"},
                                                        "shop_name": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "url": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "is_tracking": {"type": "boolean"},
                                    "is_price_change": {"type": "boolean"},
                                    "contact_methods": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "created_at": {"type": "string"},
                                    "updated_at": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            404: {"description": "No trackings found"}
        }
    }
)
def get_tracking_details():
    """Retrieves tracking records with detailed variant information."""
    user_id = request.args.get("user_id")
    tracking_id = request.args.get("tracking_id")
    
    trackings = supabase_util.get_tracking_details(user_id=user_id, tracking_id=tracking_id)
    return jsonify({"status_code": 200, "trackings": trackings})

@supabase_bp.route("/api/products", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Products"],
        "parameters": [
            {
                "name": "item_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID of the product to delete",
                "example": 24256522593
            },
            {
                "name": "user_id",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "ID of the user who owns the product",
                "example": "550e8400-e29b-41d4-a716-446655440000"
            }
        ],
        "responses": {
            200: {
                "description": "Product deleted successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {"type": "integer", "example": 200},
                        "message": {"type": "string", "example": "Product and all its variants deleted successfully"}
                    }
                }
            },
            403: {"description": "Unauthorized - User doesn't own this product"},
            404: {"description": "Product not found"},
            500: {"description": "Internal Server Error"}
        },
    }
)
def delete_product():
    """Deletes a product, all its variants, and updates any tracking references."""
    item_id = request.args.get("item_id", type=int)
    user_id = request.args.get("user_id", type=str)

    if not item_id or not user_id:
        return jsonify({"status_code": 400, "error": "Missing item_id or user_id"}), 400

    success, message, status_code = supabase_util.delete_product(item_id, user_id)
    return jsonify({"status_code": status_code, "message" if success else "error": message}), status_code

