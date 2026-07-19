@api_bp.route("/shorten", methods=["POST"])
def shorten_api():

    data = request.get_json()
    print("REQUEST DATA =", data)

    if not data or "url" not in data:
        return jsonify({
            "success": False,
            "message": "URL missing"
        }), 400

    original_url = data["url"].strip()

    alias = data.get("alias", "").strip()
    print("ALIAS RECEIVED =", alias)

    if alias:
        print("USING ALIAS")
        exists = URL.query.filter_by(short_code=alias).first()

        if exists:
            print("ALIAS ALREADY EXISTS")
            return jsonify({
                "success": False,
                "message": "Alias already exists"
            }), 400

        code = alias
    else:
        print("GENERATING RANDOM CODE")
        code = generate_code()

    print("FINAL CODE =", code)

    new_url = URL(
        original_url=original_url,
        short_code=code
    )

    db.session.add(new_url)
    db.session.commit()

    print("SAVED TO DB")

    return jsonify({
        "success": True,
        "short_code": code,
        "short_url": request.host_url.rstrip("/") + "/" + code
    })
