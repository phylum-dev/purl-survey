import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.TreeMap;

import org.sonatype.goodies.packageurl.InvalidException;
import org.sonatype.goodies.packageurl.PackageUrl;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.DatabindException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class format {
    public static void main(String[] args) throws IOException, DatabindException {
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
                Parts parts = mapper.readValue(line, Parts.class);
                TreeMap<String, String> qualifiers = null;
                if (parts.qualifiers != null) {
                    qualifiers = new TreeMap<String, String>(parts.qualifiers);
                }
                PackageUrl purl = PackageUrl.builder().type(parts.type).namespace(parts.namespace).name(parts.name).version(parts.version).qualifiers(qualifiers).subpath(parts.subpath).build();
                System.out.println(purl);
            } catch (InvalidException e) {
                Error error = new Error();
                error.error = e.toString();
                mapper.writeValue(System.out, error);
                System.out.println();
            }
        }
    }
}
