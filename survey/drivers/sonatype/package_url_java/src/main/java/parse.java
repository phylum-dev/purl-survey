import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import org.sonatype.goodies.packageurl.PackageUrl;
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
                PackageUrl purl = PackageUrl.parse(line);
                Parts parts = new Parts();
                parts.type = purl.getType();
                parts.name = purl.getName();
                parts.namespace = purl.getNamespaceAsString();
                parts.version = purl.getVersion();
                parts.qualifiers = purl.getQualifiers();
                parts.subpath = purl.getSubpathAsString();
                mapper.writeValue(System.out, parts);
            } catch (Exception e) {
                Error error = new Error();
                error.error = e.toString();
                mapper.writeValue(System.out, error);
            }
            System.out.println();
        }
    }
}
