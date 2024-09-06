from django.shortcuts import  get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Product, Order, OrderItem
from .serializers import (
    CustomerSerializer,
    OrderGetAllSerializer,
    ProductSerializer,
    OrderSerializer,
)
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError



class CustomersAPIView(APIView):

    def get(self, request):
        try:
            customers = Customer.objects.all()
            serializer = CustomerSerializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response(
                {"error": "No data found ! "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while fetching data ! : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        if not request.data:
            return Response(
                {"error": "No data provided ! "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response(
                {
                    "error": "Error while saving object !",
                    "details": str(e),
                    "data": serializer.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "error": "An unexpected error occurred !",
                    "details": str(e),
                    "data": request.data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, id):
        if not request.data:
            return Response(
                {"error": f"data is not provided ! : {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            customer = get_object_or_404(Customer, pk=id)
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response(
                {"error": f"errors while updaing object : {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "error": "An unexpected error occurred.",
                    "details": str(e),
                    "data": request.data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductAPIView(APIView):
    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"error": "No data found ! "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while fetching data ! : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        if not request.data:
            return Response(
                {"error": "No data provided ! "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response(
                {
                    "error": "Error while saving object !",
                    "details": str(e),
                    "data": serializer.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "error": "An unexpected error occurred !",
                    "details": str(e),
                    "data": request.data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderAPIView(APIView):
    def get(self, request):
        try:
            products = request.query_params.get("products")
            customer_name = request.query_params.get("customer")
            orders = Order.objects.all()

            if products:
                product_names = products.split(",")
                orders = orders.filter(
                    order_items__product__name__in=product_names
                ).distinct()

            if customer_name:
                orders = orders.filter(customer__name=customer_name)

            serializer = OrderGetAllSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {"error": "No data found ! "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred while fetching data ! : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def post(self, request):
        if not request.data:
            return Response(
                {"error": "No data provided ! "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            order_serializer = OrderSerializer(data=request.data)
            if order_serializer.is_valid(raise_exception=True):
                order_serializer.save()
                order_items = request.data.get("order_items")
                total_weight = 0

                for item in order_items:
                    product_id = item.get("product")
                    quantity = item.get("quantity")
                    product = get_object_or_404(Product, id=product_id)
                    total_weight = total_weight + product.weight * quantity
                if total_weight > 150:
                    raise ValidationError(
                        "Order cumulative weight cannot exceed 150kg."
                    )
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {
                    "error": "Error while saving object !",
                    "details": str(e),
                    "data": order_serializer.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            transaction.set_rollback(True)
            return Response(
                {
                    "error": "An unexpected error occurred !",
                    "details": str(e),
                    "data": request.data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def put(self, request, id):
        order = get_object_or_404(Order, id=id)
        order_serializer = OrderSerializer(order, data=request.data)

        try:
            if order_serializer.is_valid(raise_exception=True):
                order_items_data = request.data.get("order_items")
                total_weight = 0
                OrderItem.objects.filter(order=order).delete()

                for item in order_items_data:
                    product_id = item.get("product")
                    quantity = item.get("quantity")
                    product = get_object_or_404(Product, id=product_id)
                    total_weight += product.weight * quantity
                    OrderItem.objects.create(
                        order=order, product=product, quantity=quantity
                    )

                if total_weight > 150:
                    raise ValidationError(
                        "Order cumulative weight cannot exceed 150kg."
                    )

                order_serializer.save()

                return Response(order_serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.set_rollback(True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )