from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    # Renderiza o arquivo index.html da pasta "templates"
    return render_template("home_ecommerce.html")

if __name__ == "__main__":
    app.run(debug=True)
