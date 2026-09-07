import json
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, jsonify, abort, session, flash,
)

from app import db
from app.models import Group, Member, Expense
from app.settlement import calculate_settlements

main_bp = Blueprint('main', __name__)

CURRENCIES = [
    {'code': 'INR', 'symbol': '₹', 'name': 'Indian Rupee'},
    {'code': 'USD', 'symbol': '$', 'name': 'US Dollar'},
    {'code': 'EUR', 'symbol': '€', 'name': 'Euro'},
    {'code': 'GBP', 'symbol': '£', 'name': 'British Pound'},
    {'code': 'JPY', 'symbol': '¥', 'name': 'Japanese Yen'},
    {'code': 'AUD', 'symbol': 'A$', 'name': 'Australian Dollar'},
    {'code': 'CAD', 'symbol': 'C$', 'name': 'Canadian Dollar'},
    {'code': 'SGD', 'symbol': 'S$', 'name': 'Singapore Dollar'},
    {'code': 'AED', 'symbol': 'د.إ', 'name': 'UAE Dirham'},
    {'code': 'THB', 'symbol': '฿', 'name': 'Thai Baht'},
    {'code': 'MYR', 'symbol': 'RM', 'name': 'Malaysian Ringgit'},
    {'code': 'LKR', 'symbol': 'Rs', 'name': 'Sri Lankan Rupee'},
    {'code': 'NPR', 'symbol': 'रू', 'name': 'Nepalese Rupee'},
    {'code': 'IDR', 'symbol': 'Rp', 'name': 'Indonesian Rupiah'},
    {'code': 'PHP', 'symbol': '₱', 'name': 'Philippine Peso'},
]

CATEGORIES = [
    'Food & Drinks',
    'Transport',
    'Tickets & Entry',
    'Accommodation',
    'Prasadham & Pooja',
    'Shopping',
    'Medical',
    'Tips',
    'Other',
]


def _get_currency_symbol(code):
    for c in CURRENCIES:
        if c['code'] == code:
            return c['symbol']
    return code


def _get_group_or_404(group_uuid):
    group = Group.query.filter_by(uuid=group_uuid).first()
    if not group:
        abort(404)
    return group


def _get_session_key(group_uuid):
    return f'group_{group_uuid}'


def _get_current_member(group_uuid):
    """Retrieve the current session member info for a group, validating DB record exists."""
    session_key = _get_session_key(group_uuid)
    member_data = session.get(session_key)
    if not member_data:
        return None

    # Validate that member still exists in database
    member_id = member_data.get('member_id')
    if member_id:
        member = Member.query.get(member_id)
        if not member:
            session.pop(session_key, None)
            return None
    return member_data


def require_group_access(f):
    """Decorator that checks the user has joined this group via PIN."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        group_uuid = kwargs.get('group_uuid')
        if not _get_current_member(group_uuid):
            return redirect(url_for('main.join_group', group_name_prefill=''))
        return f(*args, **kwargs)
    return decorated_function


# ───────────────────────────────────────────
#  Landing Page
# ───────────────────────────────────────────

@main_bp.route('/')
def index():
    return render_template('index.html', currencies=CURRENCIES)


# ───────────────────────────────────────────
#  Create Group
# ───────────────────────────────────────────

@main_bp.route('/create', methods=['POST'])
def create_group():
    group_name = request.form.get('group_name', '').strip()[:100]
    currency = request.form.get('currency', 'INR').upper()
    pin = request.form.get('pin', '').strip()
    creator_name = request.form.get('creator_name', '').strip()[:50]

    if not group_name or not pin or not creator_name:
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('main.index'))

    if len(pin) < 4 or len(pin) > 6:
        flash('PIN must be 4-6 characters.', 'error')
        return redirect(url_for('main.index'))

    # Validate currency selection
    valid_currencies = {c['code'] for c in CURRENCIES}
    if currency not in valid_currencies:
        currency = 'INR'

    # Edge Case Fix: Enforce case-insensitive group name uniqueness to prevent PIN collision
    existing_group = Group.query.filter(
        db.func.lower(Group.name) == group_name.lower()
    ).first()

    if existing_group:
        flash(f'A group named "{group_name}" already exists. Please choose a unique group name or join the existing group.', 'error')
        return redirect(url_for('main.index'))

    group = Group(name=group_name, currency=currency)
    group.set_pin(pin)
    db.session.add(group)
    db.session.flush()

    creator = Member(group_id=group.id, name=creator_name)
    db.session.add(creator)
    db.session.flush()

    db.session.commit()

    session[_get_session_key(group.uuid)] = {
        'member_id': creator.id,
        'member_name': creator.name,
        'pin': pin,
    }

    return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))


# ───────────────────────────────────────────
#  Join Group
# ───────────────────────────────────────────

@main_bp.route('/join', methods=['GET', 'POST'])
def join_group():
    if request.method == 'POST':
        group_name = request.form.get('group_name', '').strip()
        pin = request.form.get('pin', '').strip()

        if not group_name or not pin:
            flash('Please enter the group name and PIN.', 'error')
            return render_template('join.html', group_name=group_name)

        group = Group.query.filter(
            db.func.lower(Group.name) == group_name.lower()
        ).first()

        if not group:
            flash('Group not found. Check the group name and try again.', 'error')
            return render_template('join.html', group_name=group_name)

        if not group.check_pin(pin):
            flash('Wrong PIN. Please try again.', 'error')
            return render_template('join.html', group_name=group_name)

        session[f'verified_{group.uuid}'] = pin
        return redirect(url_for('main.join_set_name', group_uuid=group.uuid))

    group_name_prefill = request.args.get('group_name', '')
    return render_template('join.html', group_name=group_name_prefill)


@main_bp.route('/join/<group_uuid>/set-name', methods=['GET', 'POST'])
def join_set_name(group_uuid):
    """Step 2: After PIN verified, user enters their name to join."""
    group = _get_group_or_404(group_uuid)
    verified_pin = session.get(f'verified_{group.uuid}')

    if not verified_pin:
        return redirect(url_for('main.join_group'))

    if request.method == 'POST':
        member_name = request.form.get('member_name', '').strip()[:50]

        if not member_name:
            flash('Please enter your name.', 'error')
            return render_template('join_name.html', group=group)

        existing = Member.query.filter(
            Member.group_id == group.id,
            db.func.lower(Member.name) == member_name.lower()
        ).first()

        if existing:
            session[_get_session_key(group.uuid)] = {
                'member_id': existing.id,
                'member_name': existing.name,
                'pin': verified_pin,
            }
        else:
            member = Member(group_id=group.id, name=member_name)
            db.session.add(member)
            db.session.commit()

            session[_get_session_key(group.uuid)] = {
                'member_id': member.id,
                'member_name': member.name,
                'pin': verified_pin,
            }

        session.pop(f'verified_{group.uuid}', None)
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    return render_template('join_name.html', group=group)


# ───────────────────────────────────────────
#  Group Dashboard
# ───────────────────────────────────────────

@main_bp.route('/group/<group_uuid>')
@require_group_access
def group_dashboard(group_uuid):
    group = _get_group_or_404(group_uuid)
    currency_symbol = _get_currency_symbol(group.currency)
    current_member = _get_current_member(group_uuid)

    return render_template(
        'group.html',
        group=group,
        currency_symbol=currency_symbol,
        categories=CATEGORIES,
        current_member=current_member,
    )


# ───────────────────────────────────────────
#  Expenses
# ───────────────────────────────────────────

@main_bp.route('/group/<group_uuid>/add-expense', methods=['POST'])
@require_group_access
def add_expense(group_uuid):
    group = _get_group_or_404(group_uuid)

    paid_by_raw = request.form.get('paid_by')
    amount_raw = request.form.get('amount')
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Other')
    split_among_raw = request.form.getlist('split_among')

    if not all([paid_by_raw, amount_raw, description]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    try:
        paid_by_id = int(paid_by_raw)
        amount = float(amount_raw)
    except (ValueError, TypeError):
        flash('Invalid amount or payer selection.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    if amount < 0.01 or amount > 1_000_000_000:
        flash('Amount must be between 0.01 and 1,000,000,000.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    group_member_ids = {m.id for m in group.members}
    if paid_by_id not in group_member_ids:
        flash('Selected payer is not a member of this group.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    # Parse split members and filter only active members
    split_ids = [int(sid) for sid in split_among_raw if sid.isdigit()]
    valid_split_ids = [sid for sid in split_ids if sid in group_member_ids]

    if not valid_split_ids:
        valid_split_ids = list(group_member_ids)

    expense = Expense(
        group_id=group.id,
        paid_by_id=paid_by_id,
        amount=round(amount, 2),
        description=description[:200],
        category=category,
        split_among=json.dumps(valid_split_ids),
    )
    db.session.add(expense)
    db.session.commit()

    return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))


@main_bp.route('/group/<group_uuid>/edit-expense/<int:expense_id>', methods=['POST'])
@require_group_access
def edit_expense(group_uuid, expense_id):
    group = _get_group_or_404(group_uuid)
    expense = Expense.query.filter_by(id=expense_id, group_id=group.id).first_or_404()

    paid_by_raw = request.form.get('paid_by')
    amount_raw = request.form.get('amount')
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Other')
    split_among_raw = request.form.getlist('split_among')

    if not all([paid_by_raw, amount_raw, description]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    try:
        paid_by_id = int(paid_by_raw)
        amount = float(amount_raw)
    except (ValueError, TypeError):
        flash('Invalid amount or payer selection.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    if amount < 0.01 or amount > 1_000_000_000:
        flash('Amount must be positive.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    group_member_ids = {m.id for m in group.members}
    if paid_by_id not in group_member_ids:
        flash('Selected payer is not a member of this group.', 'error')
        return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))

    split_ids = [int(sid) for sid in split_among_raw if sid.isdigit()]
    valid_split_ids = [sid for sid in split_ids if sid in group_member_ids]

    if not valid_split_ids:
        valid_split_ids = list(group_member_ids)

    expense.paid_by_id = paid_by_id
    expense.amount = round(amount, 2)
    expense.description = description[:200]
    expense.category = category
    expense.split_among = json.dumps(valid_split_ids)

    db.session.commit()
    flash('Expense updated successfully.', 'success')

    return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))


@main_bp.route('/group/<group_uuid>/delete-expense/<int:expense_id>', methods=['POST'])
@require_group_access
def delete_expense(group_uuid, expense_id):
    group = _get_group_or_404(group_uuid)
    expense = Expense.query.filter_by(id=expense_id, group_id=group.id).first()

    if expense:
        db.session.delete(expense)
        db.session.commit()

    return redirect(url_for('main.group_dashboard', group_uuid=group.uuid))


# ───────────────────────────────────────────
#  Settlement
# ───────────────────────────────────────────

@main_bp.route('/group/<group_uuid>/settle')
@require_group_access
def settle(group_uuid):
    group = _get_group_or_404(group_uuid)
    currency_symbol = _get_currency_symbol(group.currency)

    result = calculate_settlements(group.members, group.expenses)

    return render_template(
        'settlement.html',
        group=group,
        currency_symbol=currency_symbol,
        balances=result['balances'],
        settlements=result['settlements'],
        total_spent=result['total_spent'],
        max_abs_net=result.get('max_abs_net', 1.0),
    )


# ───────────────────────────────────────────
#  Leave & Delete Group
# ───────────────────────────────────────────

@main_bp.route('/group/<group_uuid>/leave', methods=['POST'])
def leave_group(group_uuid):
    session.pop(_get_session_key(group_uuid), None)
    flash('You have left the group.', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/group/<group_uuid>/delete', methods=['POST'])
@require_group_access
def delete_group(group_uuid):
    group = _get_group_or_404(group_uuid)
    group_name = group.name

    db.session.delete(group)
    db.session.commit()

    session.pop(_get_session_key(group_uuid), None)
    session.pop(f'verified_{group_uuid}', None)
    flash(f'Group "{group_name}" and all associated expenses have been permanently deleted.', 'success')
    return redirect(url_for('main.index'))


# ───────────────────────────────────────────
#  API
# ───────────────────────────────────────────

@main_bp.route('/api/group/<group_uuid>/data')
def group_data_api(group_uuid):
    group = _get_group_or_404(group_uuid)

    if not _get_current_member(group_uuid):
        return jsonify({'error': 'Unauthorized'}), 403

    currency_symbol = _get_currency_symbol(group.currency)
    result = calculate_settlements(group.members, group.expenses)

    return jsonify({
        'group': group.to_dict(),
        'currency_symbol': currency_symbol,
        'settlement': result,
    })


# ───────────────────────────────────────────
#  Error Handlers
# ───────────────────────────────────────────

@main_bp.errorhandler(404)
def page_not_found(error):
    return render_template('base.html', error_404=True), 404
