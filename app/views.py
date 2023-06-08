# App routing
from flask import Blueprint, render_template, request, jsonify, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
import socket
import scapy.all as scapy

bp = Blueprint("main", __name__)

table_data = []

def get_device_name(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return ""


def scan_local_network(interface):
    arp_request = scapy.ARP(pdst='192.168.1.0/24')
    ether = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    packet = ether / arp_request

    result = scapy.srp(packet, timeout=3, iface=interface, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({
            'ip': received[scapy.ARP].psrc,
            'mac': received[scapy.Ether].src,
            'name': get_device_name(received[scapy.ARP].psrc)
        })

    return devices


class EditForm(FlaskForm):
    macInput = StringField('MAC Address', validators=[DataRequired()])
    ipInput = StringField('IP Address', validators=[DataRequired()])
    nameInput = StringField('Name')
    managedInput = BooleanField('Managed')


bp.route('/', methods=['GET'])
def index():
    return redirect("http://grafana:3000/")

@bp.route('/scanner', methods=['GET', 'POST'])
def scanner():
    form = EditForm()
    has_selected_row = False

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the submitted row index
            row_index = request.form.get('row_index')

            # Update the table_data with the edited row
            table_data[row_index]['mac'] = form.macInput.data
            table_data[row_index]['ip'] = form.ipInput.data
            table_data[row_index]['name'] = form.nameInput.data
            table_data[row_index]['managed'] = form.managedInput.data

            # Render the template with the updated table data
            return render_template('scanner.html', form=form, has_selected_row=has_selected_row, table_data=table_data)

        else:
            return jsonify(errors=form.errors)

    if request.method == 'GET' and 'scan_network' in request.args:
        # Perform network scanning
        interface = 'Wi-Fi'
        devices = scan_local_network(interface)

        # Update the table_data with the scanned devices
        table_data.extend(devices)

        # Render the template with the updated table data
        return render_template('scanner.html', form=form, has_selected_row=has_selected_row, table_data=table_data)

    return render_template('scanner.html', form=form, has_selected_row=has_selected_row, table_data=table_data)


@bp.route('/update_table', methods=['POST'])
def update_table():
    # Process the submitted table data (e.g., filter and insert into the database)
    data = request.json.get('table_data', [])
    # Perform your data processing logic here

    return jsonify(message='Table data updated successfully')
