import io
import scrython as scry
import FreeSimpleGUI as sg
from PIL import Image
import requests as req


def main():

    card = scry.cards.Random()
    yes_list = []
    no_list = []

    # Get image
    jpg_response = req.get(card.image_uris()['normal'])
    jpg_response.raise_for_status()

    # Convert to PNG
    pil_image = Image.open(io.BytesIO(jpg_response.content))
    png_bio = io.BytesIO()
    pil_image.save(png_bio, format='PNG')

    # Initialize Window
    layout = [[sg.Column([[sg.Text("Sparks Joy:", font='bold')],
                          [sg.Listbox(values=yes_list, expand_x=True, expand_y=True, key='-YES_LIST-')],
                          [sg.Button('Yes')]],
                          vertical_alignment='top', expand_y=True),
              sg.Column([[sg.Text("Does this spark joy?")], 
                         [sg.Image(data=png_bio.getvalue(), key = '-IMAGE-')]], 
                         vertical_alignment='top'),
              sg.Column([[sg.Text("Does Not Spark Joy:", font='bold')],
                         [sg.Listbox(values=no_list, expand_x=True, expand_y=True, key='-NO_LIST-')],
                         [sg.Button('No')]],
                         vertical_alignment='top', expand_y=True)]]

    window = sg.Window('Kondo Cube Generator', layout)

    # Start App
    while True:

        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        if event == 'Yes' or event == 'No':
            if event == 'Yes':
                # Add to Yes List
                yes_list.append(card.name())
                window['-YES_LIST-'].update(yes_list)
            elif event == 'No':
                # Add to Yes List
                no_list.append(card.name())
                window['-NO_LIST-'].update(no_list)

            # Get new card and update image
            card = scry.cards.Random()
            jpg_response = req.get(card.image_uris()['normal'])
            jpg_response.raise_for_status()

            # Convert to PNG
            pil_image = Image.open(io.BytesIO(jpg_response.content))
            png_bio = io.BytesIO()
            pil_image.save(png_bio, format='PNG')

            # Update image
            window['-IMAGE-'].update(data=png_bio.getvalue())

if __name__ == '__main__':
    main()
