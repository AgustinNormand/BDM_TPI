package com.bdmhpe.scraper;

import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.JsonNode;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;
import org.apache.http.HttpStatus;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    @Value("${meli.app.id}")
    private String appId;

    @Value("${meli.secret.key}")
    private String secretKey;

    @Value("${meli.redirect.uri}")
    private String redirectUri;

    public AuthorizationInfo authorize(String code) {
        try {
            Unirest.setTimeouts(0, 0);
            HttpResponse<JsonNode> response = Unirest.post("https://api.mercadolibre.com/oauth/token")
                    .header("accept", "application/json")
                    .header("content-type", "application/x-www-form-urlencoded")
                    .field("grant_type", "authorization_code")
                    .field("client_id", appId)
                    .field("client_secret", secretKey)
                    .field("code", code)
                    .field("redirect_uri", redirectUri)
                    .asJson();
            JSONObject body = response.getBody().getObject();

            if (response.getStatus() == HttpStatus.SC_OK) {
                System.out.println(body);
                return AuthorizationInfo.success(body.getString("access_token"));
            }

            return AuthorizationInfo.failed(body.getString("error"), body.getString("message"));

        } catch (UnirestException e) {
            e.printStackTrace();
        }
        return AuthorizationInfo.failed();
    }

}