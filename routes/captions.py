from flask import Blueprint, render_template, request, session, jsonify
from routes.auth import login_required
from services.ai_service import generate_captions, generate_hashtags
from services.caption_service import (
    save_caption, get_user_captions, get_caption_by_id,
    update_caption, delete_caption, toggle_favorite, get_favorites
)

captions_bp = Blueprint('captions', __name__)

PLATFORMS = ["Instagram", "Facebook", "LinkedIn", "X (Twitter)", "YouTube"]
TONES = ["Funny", "Professional", "Creative", "Inspirational", "Emotional", "Casual", "Promotional", "Educational"]
LENGTHS = ["short", "medium", "long"]
CATEGORIES = ["Travel", "Education", "Technology", "Business", "Fashion", "Food",
               "Fitness", "Lifestyle", "Entertainment", "Motivation"]


@captions_bp.route('/generate')
@login_required
def generate_page():
    return render_template('generate.html',
                           platforms=PLATFORMS,
                           tones=TONES,
                           lengths=LENGTHS,
                           categories=CATEGORIES)


@captions_bp.route('/my-captions')
@login_required
def my_captions():
    return render_template('captions.html',
                           platforms=PLATFORMS,
                           categories=CATEGORIES)


@captions_bp.route('/hashtags')
@login_required
def hashtags_page():
    return render_template('hashtags.html', categories=CATEGORIES)


@captions_bp.route('/history')
@login_required
def history_page():
    return render_template('history.html',
                           platforms=PLATFORMS,
                           categories=CATEGORIES)


@captions_bp.route('/favorites')
@login_required
def favorites_page():
    return render_template('favorites.html')


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@captions_bp.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    topic = data.get('topic', '').strip()
    platform = data.get('platform', 'Instagram')
    category = data.get('category', 'Lifestyle')
    tone = data.get('tone', 'Creative')
    length = data.get('length', 'medium')
    keywords = data.get('keywords', '').strip()

    if not topic:
        return jsonify({"error": "Topic/description is required"}), 400
    if platform not in PLATFORMS:
        return jsonify({"error": "Invalid platform"}), 400
    if tone not in TONES:
        return jsonify({"error": "Invalid tone"}), 400
    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    try:
        captions, is_demo = generate_captions(topic, platform, category, tone, length, keywords)

        # Save all 3 to history automatically
        saved_ids = []
        for cap in captions:
            cid = save_caption(
                user_id=session['user_id'],
                platform=platform,
                category=category,
                tone=tone,
                topic=topic,
                caption_text=cap['text'],
                hashtags=cap['hashtags'],
                keywords=keywords,
                caption_length=length,
                is_saved=0
            )
            saved_ids.append(cid)

        return jsonify({
            "success": True,
            "captions": [
                {
                    "id": cid,
                    "text": cap['text'],
                    "hashtags": cap['hashtags'],
                    "char_count": len(cap['text'])
                }
                for cid, cap in zip(saved_ids, captions)
            ],
            "is_demo": is_demo,
            "platform": platform,
            "category": category,
            "tone": tone
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@captions_bp.route('/api/hashtags', methods=['POST'])
@login_required
def api_hashtags():
    data = request.get_json()
    topic = data.get('topic', '').strip()
    category = data.get('category', 'General')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        hashtags, is_demo = generate_hashtags(topic, category)
        return jsonify({"success": True, "hashtags": hashtags, "is_demo": is_demo})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@captions_bp.route('/api/captions', methods=['GET'])
@login_required
def api_get_captions():
    is_saved = request.args.get('saved')
    platform = request.args.get('platform')
    category = request.args.get('category')
    search = request.args.get('search')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))

    if is_saved is not None:
        is_saved = int(is_saved)

    captions = get_user_captions(
        user_id=session['user_id'],
        is_saved=is_saved,
        platform=platform,
        category=category,
        search=search,
        limit=limit,
        offset=offset
    )
    return jsonify({"success": True, "captions": captions})


@captions_bp.route('/api/captions/<int:caption_id>', methods=['DELETE'])
@login_required
def api_delete_caption(caption_id):
    success = delete_caption(caption_id, session['user_id'])
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Caption not found"}), 404


@captions_bp.route('/api/captions/<int:caption_id>', methods=['PUT'])
@login_required
def api_update_caption(caption_id):
    data = request.get_json()
    caption_text = data.get('caption_text')
    is_saved = data.get('is_saved')
    update_caption(caption_id, session['user_id'], caption_text=caption_text, is_saved=is_saved)
    return jsonify({"success": True})


@captions_bp.route('/api/favorites', methods=['POST'])
@login_required
def api_toggle_favorite():
    data = request.get_json()
    caption_id = data.get('caption_id')
    if not caption_id:
        return jsonify({"error": "caption_id required"}), 400
    added = toggle_favorite(session['user_id'], int(caption_id))
    return jsonify({"success": True, "added": added})


@captions_bp.route('/api/favorites', methods=['GET'])
@login_required
def api_get_favorites():
    favs = get_favorites(session['user_id'])
    return jsonify({"success": True, "captions": favs})
