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
            "user_dao": Inject(lambda: UserDAO()),
            "article_dao": Inject(lambda: ArticleDAO()),
            "post_dao": Inject(lambda: PostDAO()),
        },
    )
]


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
            "user_dao": Inject(Factory(UserDAO)),
            "article_dao": Inject(Factory(ArticleDAO)),
            "post_dao": Inject(Factory(PostDAO)),
        },
    )
]
