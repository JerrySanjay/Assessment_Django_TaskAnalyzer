from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer
from . import scoring
import json
from django.shortcuts import render
from django.http import JsonResponse

@api_view(['POST'])
def analyze(request):
    # Accept a list of task dicts
    data = request.data
    if not isinstance(data, list):
        return Response({'error': 'Expected a JSON array of tasks.'}, status=status.HTTP_400_BAD_REQUEST)

    validated = []
    for idx, item in enumerate(data):
        serializer = TaskInputSerializer(data=item)
        if not serializer.is_valid():
            return Response({'error': f'Invalid task at index {idx}', 'details': serializer.errors}, status=400)
        validated.append(serializer.validated_data)

    # optional: accept weights via query params or body
    weights = request.query_params.get('weights')
    weights_parsed = None
    if weights:
        try:
            weights_parsed = json.loads(weights)
        except Exception:
            weights_parsed = None

    results = scoring.analyze_tasks(validated, weights=weights_parsed)
    return Response(results)

@api_view(['GET'])
def suggest(request):
    # Return top 3 from last analyzed tasks (in-memory cache)
    # If no last analyzed data, ask client to POST to /analyze/ first with tasks.
    if not scoring.last_analyzed_tasks:
        return Response({'error': 'No tasks analyzed yet. POST to /api/tasks/analyze/ with tasks first.'}, status=400)
    top3 = scoring.last_analyzed_tasks[:3]
    # Provide explanations
    suggestions = []
    for t in top3:
        suggestions.append({
            'title': t.get('title'),
            'score': t.get('score'),
            'explanation': t.get('explanation')
        })
    return Response({'suggestions': suggestions})




