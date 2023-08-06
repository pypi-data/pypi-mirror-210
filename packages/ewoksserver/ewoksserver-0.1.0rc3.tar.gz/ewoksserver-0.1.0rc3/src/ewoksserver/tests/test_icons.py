def test_single_icon_png(rest_client, png_icons):
    assert_single_icon(rest_client, png_icons, ".png")


def test_single_icon_svg(rest_client, svg_icons):
    assert_single_icon(rest_client, svg_icons, ".svg")


def test_multiple_icons_png(rest_client, png_icons, default_icon_identifiers):
    assert_multiple_icons(rest_client, png_icons, ".png", default_icon_identifiers)


def test_multiple_icons_svg(rest_client, svg_icons, default_icon_identifiers):
    assert_multiple_icons(rest_client, svg_icons, ".svg", default_icon_identifiers)


def assert_single_icon(rest_client, icons, ext):
    identifier = "icon" + ext

    response = rest_client.get(f"/icon/{identifier}")
    assert response.status_code == 404

    icon1a = icons[0]
    response = rest_client.post(f"/icon/{identifier}", json=icon1a)
    data = response.get_json()
    assert response.status_code == 200, data
    assert data == icon1a

    response = rest_client.get(f"/icon/{identifier}")
    data = response.get_json()
    assert response.status_code == 200, data
    assert data == icon1a

    icon1b = icons[1]
    response = rest_client.put(f"/icon/{identifier}", json=icon1b)
    data = response.get_json()
    assert response.status_code == 200, data
    assert data == icon1b

    response = rest_client.get(f"/icon/{identifier}")
    data = response.get_json()
    assert response.status_code == 200, data
    assert data == icon1b

    response = rest_client.delete(f"/icon/{identifier}")
    data = response.get_json()
    assert response.status_code == 200
    assert data == {"identifier": identifier}

    response = rest_client.delete(f"/icon/{identifier}")
    data = response.get_json()
    assert response.status_code == 200
    assert data == {"identifier": identifier}

    response = rest_client.get(f"/icon/{identifier}")
    data = response.get_json()
    assert response.status_code == 404
    expected = {
        "identifier": identifier,
        "message": f"Icon '{identifier}' is not found.",
        "type": "icon",
    }
    assert data == expected


def assert_multiple_icons(rest_client, icons, ext, existing):
    expected = list(existing)
    for i, icon in enumerate(icons):
        identifier = f"icon{i}{ext}"
        expected.append(identifier)
        response = rest_client.post(f"/icon/{identifier}", json=icon)
        data = response.get_json()
        assert response.status_code == 200, data
        assert data == icon

    response = rest_client.get("/icons")
    data = response.get_json()
    assert response.status_code == 200, data
    assert set(data["identifiers"]) == set(expected)
