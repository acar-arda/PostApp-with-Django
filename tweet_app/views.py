from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import Post
from main_app.models import DeleteLog
import locale

locale.setlocale(locale.LC_ALL, "tr_TR.UTF-8")

def posts(request):
    posts = Post.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('posts')
    else:
        form = PostForm()
    
    return render(request, 'tweet_app/posts.html', {'posts': posts, 'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.user != request.user:
        return HttpResponseForbidden("Bu gönderiyi düzenleme yetkiniz yok.")
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            if not request.FILES.get('image'):
                form.instance.image = post.image
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)
    
    return render(request, "tweet_app/post_edit.html", {"post": post, "form": form})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.user != request.user:
        return HttpResponseForbidden("Bu gönderiyi silme yetkiniz yok.")
    
    if request.method == "POST":
        DeleteLog.objects.create(
            user=request.user,
            object_repr=str(post),
            model_name='Post'
        )
        post.delete()
        return redirect("home")
    
    return redirect("home")