from rest_framework import serializers
from .models import Customer, Product, Order, OrderItem
from datetime import datetime, date


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderGetAllSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "order_date", "address", "order_items"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["customer", "order_date", "address", "order_items"]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        instance.customer = validated_data.get("customer", instance.customer)
        instance.order_date = validated_data.get("order_date", instance.order_date)
        instance.address = validated_data.get("address", instance.address)
        instance.save()
        order_items_data = validated_data.pop("order_items")
        OrderItem.objects.filter(order=instance).delete()

        for item_data in order_items_data:
            OrderItem.objects.create(order=instance, **item_data)

        return instance
