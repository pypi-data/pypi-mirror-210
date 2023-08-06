from examples.basic_app import app

from . import configure_bovine_pub_sub


async def test_event_source():
    await configure_bovine_pub_sub(app)
    async with app.test_client() as client:
        response = await client.get("/")

        assert response
