from django.http import HttpResponse


def shopping_cart(ingredients):
    text_cart = ''
    for ingredient in ingredients:
        text_cart += (
            f'{ingredient.get("ingredient__name")} '
            f'{ingredient.get("amount")}'
            f'({ingredient.get("ingredient__measurement_unit")})\n'
        )
    response = HttpResponse(text_cart, 'text/plain,charset=utf8')
    response[
        "Content-Disposition"
    ] = "attachment; filename=shoping_cart.txt"
    return response
