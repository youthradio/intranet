from intranet import app, logger

if __name__ == "__main__":
    app.debug = app.config["DEBUG"]
    logger.info('Youth Radio Central server started. HOST: %s:%i DEBUG: %s' % (app.config["HOST"], app.config["PORT"], app.config["DEBUG"]) )

    if app.debug:
        app.run(host=app.config["HOST"], port=app.config["PORT"])
    else:
        app.run()
