import datetime
import pprint

from django import forms
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
# Create your views here.
from news.models import News

class ArticleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ['fulltext',]

class NewsView(APIView):
    def post(self, request, *args, **kwargs):
        f = NewsForm(request.data)
        if f.is_valid():
            News.objects.create(title=request.data.get("title"),
                            anons=request.data.get("anons"),
                            fulltext=request.data.get("fulltext", ""),
                            author_id=request.data.get("author"))

            return Response({'status': True})
        else:
            return Response({'status': False, 'msg': f.errors, 'err_code': 21})

    def delete(self,request, *args, **kwargs):
        n = get_object_or_404(News.objects.filter(approved=True), pk=kwargs.get('news_id', 0))
        n.delete()
        return Response({'status': True})

    def put(self, request, *args, **kwargs):
        n = get_object_or_404(News.objects.all(), pk=kwargs.get('news_id', 0))
        f = NewsForm(request.data, instance=n)
        if f.is_valid():
            f.save()
            return Response({'status': True})
        else:
            # print(f.errors)
            return Response({'status': False, 'msg': f.errors})

    def get(self, request, *args, **kwargs):

        print(request.query_params)

        if kwargs.get('news_id'):
            n = get_object_or_404(News.objects.filter(approved=True), pk=kwargs.get('news_id'))
            # print(n.__dict__)
            ret = n.__dict__
            ret.pop('_state')
            ret['d'] = datetime.datetime.now()
            return Response(ret)


        try:
            page = int(request.query_params.get("page", 0))
        except:
            page = 0
        try:
            perpage = int(request.query_params.get("perpage", 10))
            if perpage<=0 or perpage>50:
                perpage = 10
        except:
            perpage = 10


        all_n = News.objects.filter(approved=True)

        if request.query_params.get("category"):
            "1,2,3,41"
            all_n = all_n.filter(category_id__in=request.query_params.get("category").split(","))

        if request.query_params.get("title"):
            all_n = all_n.filter(title__icontains=request.query_params.get("title"))

        total = all_n.count()
        ret = []
        for n in all_n[(page*perpage):(page*perpage+perpage)]:
            ret.append({
                'id': n.id,
                'title': n.title,
                'author': n.author.username,
            })
        return Response({'total': total, "data": ret})