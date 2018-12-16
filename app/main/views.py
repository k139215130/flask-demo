from flask import render_template, abort, flash, redirect, url_for
from . import main
from .. import db
from ..models import User, Role, Post, Permission
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        print('修改成功')
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.id).all()
    return render_template('index.html', form=form, posts=posts)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about = form.about.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about.data = current_user.about
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about = form.about.data
        db.session.add(user)
        db.session.commit()
        flash('修改成功', 'success')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    #form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about.data = user.about
    return render_template('edit_profile_admin.html', form=form, user=user)
