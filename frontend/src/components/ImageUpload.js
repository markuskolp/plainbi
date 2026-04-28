import React from "react";

class ImageUpload extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      base64Data: null
    };
  }

  onChange = e => {
    debugger;
    let file = e.target.files[0];

    if (file) {
      const reader = new FileReader();
      reader.onload = this._handleReaderLoaded.bind(this);
      reader.readAsBinaryString(file);
    }
  };

  _handleReaderLoaded = e => {
    let binaryString = e.target.result;
    this.setState({
      base64Data: btoa(binaryString)
    });
  };

  render() {
    const { base64Data } = this.state;
    return (
      <div>
        <input
          type="file"
          name="image"
          id="file"
          accept=".jpg, .jpeg, .png"
          onChange={e => this.onChange(e)}
        />

        <p>base64 string: {base64Data}</p>
        <br />
        {base64Data != null && <img src={`data:image;base64,${base64Data}`} />}
      </div>
    );
  }
}

export default ImageUpload;

// todo: base64 aus Tabelle nehmen initial, wenn vorhanden
// todo: onchange, damit der Wert zurückgegeben wird zum speichern
// todo: eigene base64 Textarea/Img ersetzen durch diese Komponente
// todo: Switch zwischen "Image upload" und direkte Eingabe von base64