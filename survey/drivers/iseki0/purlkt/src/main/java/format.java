import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.DatabindException;
import com.fasterxml.jackson.databind.ObjectMapper;
import kotlin.Pair;
import space.iseki.purl.PUrl;

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
                List<String> namespace;
                if (parts.namespace == null) {
                    namespace = List.of();
                } else {
                    namespace = List.of(parts.namespace.split("/"));
                }
                List<Pair<String, String>> qualifiers = null;
                if (parts.qualifiers == null) {
                    qualifiers = List.of();
                } else {
                    qualifiers = parts.qualifiers.entrySet().stream()
                        .map(e -> new Pair<String, String>(e.getKey(), e.getValue()))
                        .collect(Collectors.toList());
                }
                PUrl purl = new PUrl.Builder()
                    .type(parts.type == null ? "" : parts.type)
                    .namespace(namespace)
                    .name(parts.name == null ? "" : parts.name)
                    .version(parts.version == null ? "" : parts.version)
                    .qualifiers(qualifiers)
                    .subpath(parts.subpath == null ? "" : parts.subpath)
                    .build();
                System.out.println(purl);
            } catch (Exception e) {
                Error error = new Error();
                error.error = e.toString();
                mapper.writeValue(System.out, error);
                System.out.println();
            }
        }
    }
}
