from django.shortcuts import render,redirect,reverse, get_object_or_404
from django.contrib.auth import authenticate,login as auth_login,logout
from .forms import SignUpForm,PhotoForm
from django.contrib.auth.models import User
from .models import (Profile, Post, Like, Dislike, Comment, Reply, Category, Subcategory, Friendship)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.generic import View, ListView, DetailView
from django.http import JsonResponse, HttpResponse
import datetime
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    return render(request,'index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.profile.gender = form.cleaned_data.get('gender')
            user.profile.country = form.cleaned_data.get('country')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            subject = 'Account has been created.'
            message = 'Thank you for register with us.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [form.cleaned_data.get('email'), ]
            # send_mail(subject, message, email_from, recipient_list)
            messages.success(request,'You have register successfully.')
            return redirect(reverse('social:login'))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


def login(request):
    if request.method == "POST":
        d = request.POST
        username = d.get('username')
        password = d.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login success.')
            return redirect(reverse('social:profile'))
        else:
            messages.error(request, 'Invalid username and password.')
            return redirect(reverse('social:login'))
    return render(request,'registration/login.html')


@login_required()
def dashboard(request):
    posts = Post.objects.filter(is_active=True).order_by("-published_date")
    # posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    paginator_obj = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator_obj.get_page(page)
    context = {
                'user': request.user, 
                'posts': posts,
                'timezone':timezone, 
                'total_pages':paginator_obj.num_pages,
                # 'categories': Category.objects.all().order_by('category_name')
                'categories': CATEGORIES,
                'active_class': 'dashboard'
            }
    return render(request,'dashboard.html', context)


@login_required()
def profile(request):
    user = request.user
    return render(request,'profile.html',{'user':user, 'active_class': 'profile'})


@login_required()
def editProfile(request):
    u_id = request.user.id
    user = request.user
    if request.method == 'POST':
        d =request.POST.get
        image = request.FILES.get('image')
        form = PhotoForm(request.POST, request.FILES)
        if image:
            if form.is_valid():
                form.save()
                return redirect('photo_list')
            else:
                form = PhotoForm()
            return render(request, 'album/photo_list.html', {'form': form, 'photos': image})
        first_name=d('first_name');last_name=d('last_name');gender=d('gender');email=d('email')
        birth_date = d('birth_date'); city = d('city'); state = d('state'); country = d('country');address = d('address')
        if first_name != '':
            messages.success(request, 'Profile update successfully.')
        if last_name!= '':
            messages.success(request, 'Profile update successfully.')
        if email != '':
            messages.success(request, 'Profile update successfully.')
        if birth_date != '':
            messages.success(request, 'Profile update successfully.')
        if gender != '':
            messages.success(request, 'Profile update successfully.')
        if city != '':
            messages.success(request, 'Profile update successfully.')
        if state != '':
            messages.success(request, 'Profile update successfully.')
        if country != '':
            messages.success(request, 'Profile update successfully.')
        if address != '':
            messages.success(request, 'Profile update successfully.')
        return redirect('social:profile')

    return render(request,'editProfile.html',{'user':user})


@login_required
def forgot_password(request):
    if request.method == 'POST':
        u_email= request.POST.get('email')
        user = User.objects.filter(email=u_email).first()
        if user is not None:
            subject = 'Your account details'
            message = 'Your username is '
            email_from = settings.EMAIL_HOST_USER
            recipient_list = ['@gmail.com', ]
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, 'User email-id found.')
        else:
            messages.warning(request, 'User not register. Please register first.')
            return redirect('social:signup')
    return render(request,'registration/forgot_password.html')


@login_required
def create_post(request):
    if request.method == "POST":
        post = request.POST.get('post-content')
        title = request.POST.get('post-title')
        category = request.POST.get('category').lower()
        subcategory = request.POST.get('subcategory').lower()
        try:
            category_obj = get_object_or_404(Category, category_name=category)
            subcategory_obj = get_object_or_404(Subcategory, category_name=category_obj, subcategory_name=subcategory)
        except:

            messages.error(request, 'Post creation failed due to invalid input.')
            return redirect(reverse('social:blog'))
        else:
            if post.strip() and title.strip() and category.strip() and subcategory.strip():
                user_obj = User.objects.get(username=request.user)
                obj = Post(
                    author= user_obj,
                    title = title.strip(),
                    text = post.strip(),
                    created_date = timezone.now(),
                    # published_date = timezone.now(),
                    category = category_obj,
                    subcategory = subcategory_obj
                )
                obj.save()
                obj.publish()
                return redirect(reverse("social:blog"))
            messages.error(request, 'Post creatioon failed due to invalid input.')
            return redirect(reverse('social:blog'))
    return redirect(reverse('social:blog'))
    


@method_decorator(login_required, name="dispatch")
class AjaxRequests(View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get('id', None)
        request_type = request.POST.get('request_type', None)
        if request_type is not None:
            if request_type == 'delete':
                if id:
                    obj = Post.objects.get(id=id.strip())
                    if obj:
                        obj.delete()
                        data = {"deleted": True}
                        return JsonResponse(data)
                    else:
                        data = {"deleted": False}
                        return JsonResponse(data)
                else:
                    data = {"deleted": False}
                    return JsonResponse(data)
            elif request_type == 'update':
                title = request.POST.get('title', None)
                content = request.POST.get('content', None)
                obj = Post.objects.get(id=id)
                obj.title = title
                obj.text = content
                obj.save()
                obj.publish()
                obj.refresh_from_db()
                data = {
                    'title': obj.title,
                    'text': obj.text,
                    'published_date': obj.published_date.strftime('%b. %d, %Y, %I:%M %p'),
                    'updated': True
                }
                return JsonResponse(data)


@method_decorator(login_required, name="dispatch")
class LikeDislike(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        user_id = request.user.id
        action = request.POST.get('action')
        post_obj = Post.objects.get(id=post_id)
        user_obj = User.objects.get(id=user_id)
        dislike = False
        try:
            dislike_obj = get_object_or_404(Dislike, post=post_obj, user=user_obj)
            if dislike_obj:
                dislike = True
            else:
                dislike = False
        except:
            dislike = False

        if action == "like":
            Like.objects.create(post=post_obj, user=user_obj)
            like_counts = post_obj.likes.count()

            if dislike:
                dislike_obj.delete()
                dislike_counts = post_obj.dislikes.count()
                data = {
                    'dislike_count': dislike_counts,
                    'like_count': like_counts,
                    'dislike': True
                }
                return JsonResponse(data)
            else:
                data = {
                    'like_count': like_counts,
                }
                return JsonResponse(data)
        elif action == "dislike":
            obj = Like.objects.filter(Q(post=post_obj) & Q(user=user_obj))
            if obj:
                obj.delete()
            data = {
                    'like_count': post_obj.likes.count(),
                }
            return JsonResponse(data)


@method_decorator(login_required, name="dispatch")
class DislikeView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        user_id = request.user.id
        action = request.POST.get('action')
        post_obj = Post.objects.get(id=post_id)
        user_obj = User.objects.get(id=user_id)
        like = False
        try:
            like_obj = get_object_or_404(Like, post=post_obj, user=user_obj)
            if like_obj:
                like = True
            else:
                like = False
        except:
            like = False
        if action == "like":
            Dislike.objects.create(post=post_obj, user=user_obj)
            dislike_counts = post_obj.dislikes.count()
            if like:
                like_obj.delete()
                like_counts = post_obj.likes.count()
                data = {
                    'dislike_count': dislike_counts,
                    'like_count': like_counts,
                    'like': True
                }
                return JsonResponse(data)
            else:
                data = {
                    'dislike_count': dislike_counts
                }
                return JsonResponse(data)
        elif action == "dislike":
            obj = get_object_or_404(Dislike, post=post_obj, user=user_obj)
            if obj:
                obj.delete()
            data = {
                    'dislike_count': post_obj.dislikes.count()
                }
            return JsonResponse(data)


@method_decorator(login_required, name="dispatch")
class CommentView(View):
    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        comment_message = request.POST.get('comment')
        user_id = request.user.id
        post_obj = Post.objects.get(id=post_id)
        user_obj = User.objects.get(id=user_id)
        obj = Comment(post_id=post_obj.id, user_id=user_obj.id, message=comment_message)
        obj.save()
        data = {
            'comment_id': obj.id,
            'commentor_username': obj.user.username,
            'comment_user_fname': obj.user.first_name.title(),
            'comment_user_lname': obj.user.last_name.title(),
            'comment_message': obj.message,
            'comment_commented_at': obj.commented_at,
            'total_comments': post_obj.comment_set.all().count(),
            'commentor_id': obj.user.pk
        }
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class ReplyToCommentView(View):
    def post(self, request, *args, **kwargs):
        comment_id = request.POST.get('comment_id').strip()
        comment_obj = get_object_or_404(Comment, id=comment_id)
        user_obj = User.objects.get(id=request.user.id)
        reply = request.POST.get('reply').strip()
        obj = Reply(user=user_obj, comment=comment_obj, message=reply)
        obj.save()
       
        data = {
            'reply_id': obj.id,
            'reply_user_fname': obj.user.first_name.title(),
            'reply_user_lname': obj.user.last_name.title(),
            'reply_message': obj.message,
            'reply_commented_at': obj.replied_at,
            'total_replies': comment_obj.reply_set.all().count(),
            'replier_id': obj.user.pk


        }
        return JsonResponse(data)


@login_required
def remove_comment(request):
    post_id = request.POST.get('post_id')
    comment_id = request.POST.get('comment_id')
    post_obj = get_object_or_404(Post, id=post_id)
    obj = get_object_or_404(Comment, id=comment_id, post=post_obj)
    obj.delete()
    data = {
        'deleted': True,
        'total_comments': post_obj.comment_set.all().count()
    }
    return JsonResponse(data)


@login_required
def remove_reply(request):
    post_id = request.POST.get('post_id')
    comment_id = request.POST.get('comment_id')
    reply_id = request.POST.get('reply_id')
    post_obj = get_object_or_404(Post, id=post_id)
    comment_obj = get_object_or_404(Comment, id=comment_id)
    obj = get_object_or_404(Reply, id=reply_id)
    obj.delete()
    data = {
        'deleted': True,
        'total_replies': comment_obj.reply_set.all().count()
    }
    return JsonResponse(data)


@login_required
def post_details(request, *args, **kwargs):
    categories_for_thumbnails = set()
    post_obj = get_object_or_404(Post, id=kwargs.get('pk'))
    category_queryset = Category.objects.all()
    for category in category_queryset:
        categories_for_thumbnails.add(category.category_name)
    context = {
                'post': post_obj,
                'categories_post': sorted(categories_for_thumbnails)
            }
    return render(request, 'post_details.html', context)


@login_required
def add_subcategory(request):
    subcategories = set()
    category = request.GET.get('category').strip()
    category_obj = Category.objects.get(category_name=category)
    subcategories_queryset = Subcategory.objects.filter(category_name=category_obj)
    for subcategory in subcategories_queryset:
        subcategories.add(subcategory.subcategory_name.title())
    data = {
        'subcategories': sorted(subcategories)
    }
    return JsonResponse(data)


@login_required
def blog(request, *args, **kwargs):
    categories_for_thumbnails = set()
    category_queryset = Category.objects.all()
    for category in category_queryset:
        categories_for_thumbnails.add(category.category_name)
    context = {}
    category = kwargs.get('key')
    if category is not None:
        try:
            category_obj = Category.objects.get(category_name=category)
        except: 
            if category == 'my_blogs':
                my_blogs_obj = Post.objects.filter(author_id=request.user.id, is_active=True).order_by('-published_date')
                if my_blogs_obj.count() == 0:
                    # posts = Post.objects.filter(is_active=True).order_by("-published_date")
                    # paginator_obj = Paginator(posts, 5)
                    context['invalid_or_unavailable_category'] = True
                    context['categories_post'] = sorted(categories_for_thumbnails)
                    # context['total_pages'] = paginator_obj.num_pages
                    context['higlight_category'] = category
                else:
                    num_posts = my_blogs_obj.count()
                    paginator_obj = Paginator(my_blogs_obj, 5)
                    page = request.GET.get('page')
                    posts = paginator_obj.get_page(page)
                    context['posts'] = posts
                    context['num_posts'] = num_posts
                    context['total_pages'] = paginator_obj.num_pages
                    context['higlight_category'] = category
                    context['categories_post'] = sorted(categories_for_thumbnails)
            else:
                messages.error(request, 'Invalid category.')
                return redirect(reverse('social:blog'))
        else:

            posts = Post.objects.filter(category=category_obj)
            if posts.count() == 0:
                # posts = Post.objects.filter(is_active=True).order_by("-published_date")
                # paginator_obj = Paginator(posts, 5)
                context['invalid_or_unavailable_category'] = True
                context['categories_post'] = sorted(categories_for_thumbnails)
                # context['total_pages'] = paginator_obj.num_pages
                context['higlight_category'] = category
            else:
                num_posts = posts.count()
                paginator_obj = Paginator(posts, 5)
                page = request.GET.get('page')
                posts = paginator_obj.get_page(page)
                context['num_posts'] = num_posts
                context['posts'] = posts
                context['higlight_category'] = category
                context['total_pages'] = paginator_obj.num_pages
                context['categories_post'] = sorted(categories_for_thumbnails)
    elif not kwargs:
        posts = Post.objects.filter(is_active=True).order_by('-published_date')
        num_posts = posts.count()
        paginator_obj = Paginator(posts, 5)
        page = request.GET.get('page')
        posts = paginator_obj.get_page(page)
        context['num_posts'] = num_posts
        context['posts'] = posts
        context['total_pages'] = paginator_obj.num_pages
        context['categories_post'] = sorted(categories_for_thumbnails)
    # context['comment-count'] = 
    context['key'] = category
    return render(request,'blogs.html', context)


@login_required
def create_category(request):
    if request.method == 'POST':
        category = request.POST.get('category-name').lower()
        subcategory = request.POST.get('subcategory-name').lower()
        if category.strip() and subcategory.strip():
            try:
                category_obj = Category.objects.get(category_name=category)
            except:
                category_obj = Category.objects.create(category_name=category)
            subcategory_obj = Subcategory.objects.create(category_name=category_obj, subcategory_name=subcategory)
            messages.success(request, 'Category and subcategory created successfully!')
            return redirect(reverse('social:blog'))
        messages.error(request, 'Category creation failed due to invalid input.')
        return redirect(reverse('social:blog'))
        

@method_decorator(login_required, name="dispatch")
class SearchResultsView(ListView):
    model = Profile
    template_name = 'search_results.html'

    def get_context_object_name(self, queryset):
        return 'users_list'

    def get_queryset(self, *args, **kwargs):
        query = self.request.GET.get('query')
        gender = self.request.GET.get('filter-gender')
        city = self.request.GET.get('filter-location')
        default_filters = Q()
        if query.strip():
            for each in query.split():
                default_filters |= (Q(user__first_name__icontains=each)|
                                    Q(user__last_name__icontains=each)
                    )
        filters = {
            'gender': gender,
            'city': city
        }
        search_filters = dict(filter(lambda item: item[1], filters.items()))
        return Profile.objects.filter(default_filters & Q(**search_filters))
        

    def get_context_data(self, **kwargs):
        city = self.request.GET.get('filter-location')
        gender = self.request.GET.get('filter-gender')
        query = self.request.GET.get('query')
        context = super().get_context_data(**kwargs)
        context['query'] = query
        context['gender'] = gender
        context['location'] = city
        context['current_year'] = timezone.now().year
        users = self.get_queryset()
        return context


@method_decorator(login_required, name="dispatch")
class FriendProfile(DetailView):
    model = Profile
    template_name = 'friend_profile.html'
    context_object_name  = 'user_obj'

    # def get_context_object_name(self, queryset):
    #     return 'user'

  
def edit_comment(request):
    comment_id = request.POST.get('comment_id')
    edited_comment = request.POST.get('edited_comment')
    Comment.objects.filter(id=comment_id).update(message=edited_comment)
    obj = Comment.objects.get(id=comment_id)
    data = {
        'edited_comment': obj.message
    }
    return JsonResponse(data)


def edit_reply(request):
    reply_id = request.POST.get('reply_id')
    edited_reply = request.POST.get('edited_reply')
    Reply.objects.filter(id=reply_id).update(message=edited_reply)
    obj = Reply.objects.get(id=reply_id)
    data = {
        'edited_reply': obj.message
    }
    return JsonResponse(data)



# *******************************************************
# *********************Friends module********************
# *******************************************************

@login_required
def friend_list(request, *args, **kwargs):
    current_user = request.user #for more readability only
    friend_list_request_from = Friendship.objects.filter(Q(request_from=current_user) & Q(is_friend=True)).order_by('-timestamp')
    friend_list_request_to = Friendship.objects.filter(Q(request_to=current_user) & Q(is_friend=True)).order_by('-timestamp')
    non_friend_list = Friendship.objects.filter(request_to=current_user, is_friend=False).order_by('-timestamp')
    sent_request_list = Friendship.objects.filter(request_from=current_user, is_friend=False).order_by('-timestamp')
    context = {
        'friend_list_request_from': friend_list_request_from,
        'friend_list_request_to': friend_list_request_to,
        'non_friend_list': non_friend_list
        }
    return render(request, 'friends_list.html', context)


@login_required
def add_friend(request, *args, **kwargs):
    current_user = request.user #for more readability only
    friend_obj = get_object_or_404(User, pk=kwargs.get('pk'))
    Friendship.objects.get_or_create(request_from=current_user, request_to=friend_obj)
    return JsonResponse({'request': 'sent'})


@login_required
def undo_request(request, *args, **kwargs):
    current_user = request.user #for more readability only
    friend = get_object_or_404(User, pk=kwargs.get('pk'))
    obj = Friendship.objects.get(request_from=current_user, request_to=friend)
    obj.delete()
    return JsonResponse({'request': 'canceled'})


@login_required
def request_approve(request, *args, **kwargs):
    current_user = request.user #for more readability only
    friend_obj = get_object_or_404(User, pk=kwargs.get('pk'))
    obj = Friendship.objects.get(request_from=friend_obj, request_to=current_user)
    obj.make_friend()
    return JsonResponse({'request': 'approved'})
