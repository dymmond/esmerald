from esmerald import Factory, Include, Inject

route_patterns = [
    Include(
        "/api/v1",
        routes=[
            Include("/accounts", namespace="accounts.v1.urls"),
            Include("/articles", namespace="articles.v1.urls"),
            Include("/posts", namespace="posts.v1.urls"),
        ],
        interceptors=[LoggingInterceptor],  # Custom interceptor
        dependencies={
            "user_dao": Inject(Factory("myapp.accounts.daos.UserDAO")),
            "article_dao": Inject(Factory("myapp.articles.daos.ArticleDAO")),
            "post_dao": Inject(Factory("myapp.posts.daos.PostDAO")),
        },
    )
]
