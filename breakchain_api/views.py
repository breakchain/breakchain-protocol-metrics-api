from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from . import dashboardMetrics, stakingMetrics, bondingMetrics


# Create your views here.

@api_view(["GET"])
def dashboard_metrics(request):
    if request.method == 'GET':
        return JsonResponse(dashboardMetrics.get_dashboard_metrics())
    else:
        return JsonResponse({'message': "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def staking_metrics(request):
    if request.method == 'GET':
        return JsonResponse(stakingMetrics.get_staking_metrics())
    else:
        return JsonResponse({'message': "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def bonding_metrics(request):
    if request.method == 'GET':
        return JsonResponse(bondingMetrics.get_bonding_metrics())
    else:
        return JsonResponse({'message': "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)