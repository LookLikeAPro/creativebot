import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public void handle(HttpServletRequest httpRequest, HttpServletResponse httpResponse) throwsIOException, ServletException {
      // Only handle POST requests
      if (HttpMethod.POST.name().equals(httpRequest.getMethod())) {
          // 1. Read the validate.token query parameter from HTTP request
          String validateToken = httpRequest.getParameter("validate.token");

          // 2. Read the X-Yahoo-Signature header from HTTP request
          // This is the encrypted payload. Encrypted using shared BOT SECRET (https://ai.search.yahoo.com/bots/<bot_id>/settings)
          String encoded = httpRequest.getHeader("X-Yahoo-Signature");

          // 3. Read the payload from HTTP request body. This will be plain text.
          StringWriter writer = new StringWriter();
          IOUtils.copy(httpRequest.getInputStream(), writer, "UTF-8");
          String payload = writer.getBuffer().toString();
          logger.info("Got request: {}", payload);
          try {
              // 4. Validate if the request is from Yahoo A.I. Studio
              if (validate(payload, encoded)) {
                  int statusCode = Response.SC_OK;
                  // 5. Check if this is a validation request. Do not invoke fulfiller if this is a Fulfiller Trust Call (http://developer.yahoo.com/prestobots/docs/bot-workshop/about-fulfillers/#remote-fulfiller-trust-validation)
                  if (StringUtils.isEmpty(validateToken)) {
                      // This is not a Fulfiller Trust Call, but an actual fulfiller call.
                      // Invoke Fulfiller
                      Pair<String, Integer> result = callFulfiller(payload);
                      payload = result.getLeft();
                      statusCode = result.getRight();
                  }
                  // 6. Send response to Yahoo A.I. Studio
                  httpResponse.getWriter().write(payload);
                  httpResponse.setStatus(statusCode);
              } else {
                  // 7. Validation failed, cannot trust the caller. Send error response.
                  Error error = new Error();
                  error.setError("Bad token");
                  httpResponse.getWriter().write(mapper.writeValueAsString(error));
                  httpResponse.setStatus(Response.SC_UNAUTHORIZED);
              }
          } catch (Exception e) {
              logger.error("Exception ", e);
              Error error = new Error();
              error.setError(e.getMessage());
              httpResponse.getWriter().write(mapper.writeValueAsString(error));
              httpResponse.setStatus(Response.SC_INTERNAL_SERVER_ERROR);
          }
      } else {
          Error error = new Error();
          error.setError("Only POST method is allowed");
          httpResponse.getWriter().write(mapper.writeValueAsString(error));
          httpResponse.setStatus(Response.SC_BAD_REQUEST);
      }
      // Always send Content-Type header as application/json
      httpResponse.setContentType(MediaType.JSON_UTF_8.toString());
      httpResponse.flushBuffer();
  }


private static boolean validate(String payload, String encoded) throws NoSuchAlgorithmException, InvalidKeyException {
      // fulfiller.algo is HmacSHA256
      String algo = ConfigManager.config.getString("fulfiller.algo");
      Mac crypto = Mac.getInstance(algo);
      // fulfiller.key is the shared BOT SECRET (https://ai.search.yahoo.com/bots/<bot_id>/settings)
      SecretKeySpec secret_key = newSecretKeySpec(ConfigManager.config.getString("fulfiller.key").getBytes(), algo);
      crypto.init(secret_key);
      String encoded1 = BaseEncoding.base16().encode(crypto.doFinal(payload.getBytes()));
      return encoded.equals(encoded1);
  }