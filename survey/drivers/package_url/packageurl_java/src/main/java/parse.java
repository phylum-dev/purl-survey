import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import com.github.packageurl.MalformedPackageURLException;
import com.github.packageurl.PackageURL;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.ObjectMapper;

public class parse {
    public static void main(String[] args) throws IOException {
        BufferedReader s = new BufferedReader(new InputStreamReader(System.in));
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(JsonGenerator.Feature.AUTO_CLOSE_TARGET, false);
        while (true) {
            String line = s.readLine();
            if (line == null) {
                break;
            }
            line = line.trim();
            if (line.isEmpty()) {
                continue;
            }
            try {
                PackageURL purl = new PackageURL(line);
                Parts parts = new Parts();
                parts.type = purl.getType();
                parts.name = purl.getName();
                parts.namespace = purl.getNamespace();
                parts.version = purl.getVersion();
                parts.qualifiers = purl.getQualifiers();
                parts.subpath = purl.getSubpath();
                mapper.writeValue(System.out, parts);
            } catch (MalformedPackageURLException e) {
                Error error = new Error();
                error.error = e.toString();
                mapper.writeValue(System.out, error);
            } catch (NullPointerException e) {
                Error error = new Error();
                error.error = e.toString();
                mapper.writeValue(System.out, error);
            }
            System.out.println();
        }
    }
}
