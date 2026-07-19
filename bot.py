@api_bp.route("/shorten", methods=["POST"])
def shorten_api():

    print("=" * 60)
    print("NEW REQUEST")

    data = request.get_json()
    print("REQUEST DATA =", data)

    if not data:
        print("ERROR: No JSON received")
        return jsonify({
            "success": False,
            "message": "No JSON"
        }), 400

    if "url" not in data:
        print("ERROR: URL missing")
        return jsonify({
            "success": False,
            "message": "URL missing"
        }), 400

    original_url = data["url"].strip()
    alias = data.get("alias", "").strip()

    print("URL =", original_url)
    print("ALIAS =", alias)

    if alias:
        print("CHECKING ALIAS IN DATABASE...")

        exists = URL.query.filter_by(short_code=alias).first()

        print("ALIAS EXISTS =", exists)

        if exists:
            print("ALIAS ALREADY USED")

            return jsonify({
                "success": False,
                "message": "Alias already exists"
            }), 400

        code = alias
        print("USING CUSTOM ALIAS =", code)

    else:
        print("NO ALIAS, GENERATING RANDOM CODE")
        code = generate_code()

    print("FINAL SHORT CODE =", code)

    new_url = URL(
        original_url=original_url,
        short_code=code
    )

    print("ADDING TO DATABASE...")
    db.session.add(new_url)
    db.session.commit()
    print("DATABASE COMMIT SUCCESS")

    short_url = request.host_url.rstrip("/") + "/" + code

    print("RETURNING SHORT URL =", short_url)
    print("=" * 60)

    return jsonify({
        "success": True,
        "short_code": code,
        "short_url": short_url
    })
